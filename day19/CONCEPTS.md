# 延伸知識：`async`/`await` 在解決什麼問題，跟多執行緒/多行程差在哪

## 先講結論：`asyncio` 解決的是「等待」，不是「算得更快」

這天的核心體感是：三個各要等 0.2 秒的查詢，依序執行要 0.6 秒，用 `asyncio.gather` 同時執行只要約 0.2 秒。**這不是因為 CPU 算得更快了**——`asyncio.sleep(0.2)` 本身不消耗 CPU，它就是「單純等待 0.2 秒」。真正發生的事情是：Python 在第一個 `check_price` 呼叫 `await asyncio.sleep(0.2)` 之後，**沒有傻傻卡在那裡等**，而是把控制權交還給一個叫 event loop（事件迴圈,持續檢查「現在有哪些任務已經準備好可以繼續執行」的排程器）的東西，讓它趁這段空檔去執行第二個、第三個查詢——三個查詢的「等待」時間互相重疊，而不是排隊疊加。**`asyncio` 適合的場景是「程式大部分時間在等某個外部的東西回應」（等網路、等對方系統、等磁碟 I/O），不適合「程式大部分時間在讓 CPU 算東西」**——後者是多行程（multiprocessing，真正利用多顆 CPU 核心平行運算）該解決的問題，跟 `asyncio` 是完全不同的工具，這天不展開。

## `async def`、`await`、coroutine（協程）分別是什麼

- `async def check_price(...):` 定義的不是一個普通函式，是一個 coroutine function——呼叫它（`check_price("S01", 1.0, 0.2)`）並**不會**立刻執行函式內容，只會拿到一個 coroutine 物件（可以想成「一份還沒被執行的任務說明書」）。這是新手最容易卡住的地方：直接呼叫一個 `async def` 函式，看起來什麼都沒發生，因為你只是拿到了任務說明書，還沒有人真正去執行它。
- `await` 才是「真正去執行、並等待這個 coroutine 完成」的動作，而且只能寫在另一個 `async def` 函式**內部**。
- `asyncio.run(coroutine)` 是最外層的入口——它負責建立 event loop、把你給它的 coroutine 丟進去執行、執行完畢後關掉 event loop。**這也是為什麼這天的測試不需要額外的第三方套件（例如 `pytest-asyncio`）：測試函式本身維持一般的 `def test_xxx():`（同步函式），內部用 `asyncio.run(check_all(...))` 去驅動 async 程式碼，拿到的就是一般的回傳值,可以直接用一般的 `assert` 檢查**——這是不想額外裝套件時,最直接可行的做法。

## `asyncio.gather`：同時發起多個 coroutine，一起等結果

```python
results = await asyncio.gather(*(check_price(store, price, delay) for store, price, delay in jobs))
```

`asyncio.gather(*coroutines)` 把好幾個 coroutine 一次性交給 event loop，讓它們的等待時間互相重疊，`gather` 會等到**全部**都完成才回傳一個 list（順序跟你傳入的順序一致，不是誰先完成誰排前面）。這是這天測時間差的關鍵：三個 `check_price` 呼叫的 `await asyncio.sleep(0.2)` 是同時在等，`gather` 等的是「最慢的那一個」，不是三個時間相加。

## `time.sleep()` 混進 `async def` 裡：能跑，但整個 async 的意義消失了

```python
async def check_price(store: str, price: float, delay: float) -> tuple[str, float]:
    time.sleep(delay)   # 地雷：這裡應該是 await asyncio.sleep(delay)
    return store, price
```

這段程式碼**完全不會報錯，也會得到正確的回傳值**——這正是它危險的地方。`time.sleep()` 是一般的、會真正把整個程式（包括 event loop 本身）卡住的等待，跟 `asyncio.sleep()` 不同：`asyncio.sleep()` 在等待期間會把控制權交還給 event loop，讓其他 coroutine 有機會執行；`time.sleep()` 完全不會，它會讓**當前這整個程式**（不只是這個函式）停在那裡什麼都不能做,直到時間到。結果是：三個查詢看起來仍然「同時」被發起、程式表面上完全正常執行完畢，但因為每個 `check_price` 執行到 `time.sleep()` 時把所有其他任務都卡住了,實際上變回了排隊等待——**總耗時會退化回跟依序執行差不多，只是你從回傳值完全看不出來哪裡錯了，因為結果是對的,只有「快不快」這個不會被一般測試檢查到的性質壞掉了。** 這正是這天要求「總耗時要明顯小於相加」這個測試的意義：光看回傳值對不對，抓不到這個地雷；只有真的量時間，才能抓到。**這也是 AI 生成 async 程式碼很常出現的問題**——AI 有時會把一般同步函式改成 `async def`，卻忘了把裡面所有「等待」的呼叫也換成對應的 async 版本，看起來像是做了 async 化，實際上完全沒有拿到任何好處。

## `asyncio.gather` 其實有兩種失敗模式，這天只要求寫其中一種

`check_all` 用的是預設模式（不加 `return_exceptions`）：只要任何一個 coroutine 拋出例外，`gather` 立刻把那個例外往外傳播——其他還在跑的 coroutine 不會被強制中斷,但你拿不到它們的結果,程式的控制流程直接跳到例外處理那一段。這叫 fail-fast，**適合「其中一次查詢失敗,代表整批結果都不該被信任」的情境**，跟 final_project 規格裡「required item 沒全部 priced 就整個 baseline 判定失敗」是同一種設計精神。

`asyncio.gather(..., return_exceptions=True)` 是另一種模式：不管每個 coroutine 成功還是拋例外，`gather` 都會等全部結束，回傳的 list 裡失敗的位置會是那個例外物件本身,而不是往外拋出，你需要自己動手把例外跟正常結果分開組裝。**這適合「一間店查詢失敗,不該讓其他 29 間店的結果也拿不到」的情境**——這是一個報告工具而不是一個嚴格驗證工具時，比較合理的預設行為。這天不要求你也實作這個版本（免得同一天要寫兩套幾乎一樣的邏輯），但知道這個參數存在，之後看到 AI 生成的 `gather` 呼叫時，會知道去檢查它有沒有加這個參數，以及加或不加對應的是哪一種產品行為。

## 如果真的有一段「等待」是包在一個只能同步呼叫的函式裡呢

`time.sleep()` 的地雷告訴你「async 函式裡要用 `asyncio.sleep()`，不能用會卡住整個程式的同步等待」——但現實中你常常會遇到一個第三方函式庫，它某個會花時間等待的函式（例如讀一個很大的檔案、呼叫一個沒有提供 async 版本的網路函式庫）**只提供同步版本**，你沒辦法把它內部換成 `await asyncio.sleep()`，因為那是別人寫的程式碼，不是你能改的。這時候標準庫提供 `asyncio.to_thread()`：

```python
async def check_price(store: str, price: float, delay: float) -> tuple[str, float]:
    await asyncio.to_thread(time.sleep, delay)   # 把同步呼叫丟到另一個執行緒跑
    return store, price
```

`asyncio.to_thread(某個同步函式, *參數)` 把那個同步函式丟到另一個執行緒（thread）去執行，`await` 的是「等那個執行緒跑完」，這段等待期間 event loop 一樣可以去處理其他 coroutine——**效果跟你自己把整段邏輯改寫成 `asyncio.sleep()` 一樣，但不需要去改那個你改不了的同步函式**。這是「已經有一堆別人寫好的同步程式碼，想在 async 專案裡使用又不想整份重寫」時的標準解法，這天不要求用到（`asyncio.sleep()` 已經是原生 async，不需要繞這一圈），但看到 AI 生成的 async 程式碼裡出現 `asyncio.to_thread`，現在你知道它在解決什麼問題：包住一段沒有 async 版本、但又不想讓它卡住 event loop 的同步呼叫。

## 真實世界裡，`asyncio` 實際會用在什麼地方

- **同時打多個 API/HTTP 請求**：例如同時查詢多個外部服務的狀態，不想一個一個依序等回應。
- **WebSocket 或需要同時維持大量連線的伺服器**：像聊天伺服器需要同時「聽」很多個客戶端,傳統的一個執行緒對應一個連線的做法在連線數很多時會很吃資源，async 讓單一執行緒就能同時應付大量「大部分時間在等待」的連線。
- **跟 day09 的 subprocess 銜接**：`asyncio.create_subprocess_exec()` 是 `subprocess.run()` 的 async 版本——如果你要對 50 個 git repo 各跑一次 `git status`，用 day09 教的 `subprocess.run()` 要一個一個依序等；換成 `asyncio.create_subprocess_exec()` 搭配 `asyncio.gather()`，可以同時對 50 個 repo 發起,等待時間互相重疊。這天沒有要求動手做這個（範圍會太大），但知道這個銜接點存在，之後遇到「要同時對很多東西跑外部指令」的需求時，會知道 `asyncio` 是其中一個工具選項。
- **不適合的情境**：純粹的數值運算（例如把很大的資料集全部載入記憶體算統計）不會因為改成 async 而變快——這種情境如果真的需要平行加速，該找的是 `multiprocessing`（多行程，真正用上多顆 CPU 核心）,不是 `asyncio`。看到 AI 建議把一段吃 CPU 的計算改寫成 `async def` 來加速，值得先確認這段程式碼實際上是在「等待」還是在「計算」——這正是判斷 async 適不適用的分界線。
