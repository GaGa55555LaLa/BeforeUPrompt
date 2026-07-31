# 延伸知識：呼叫外部程式時，你其實是在管理一個信任邊界

## `shell=True` 的風險：不是「比較危險」，是「直接開一個洞」

```python
subprocess.run(f"git log {branch}", shell=True)   # 危險
subprocess.run(["git", "log", branch])              # 安全
```

`shell=True` 會把整個字串交給系統的 shell（`bash`/`sh`）去解析執行，這代表字串裡任何 shell 語法（`;`、`&&`、`` ` ``、`$()`）都會被當成指令執行，不是當成純文字參數。如果 `branch` 這個變數的內容是使用者輸入、或來自檔案、或來自任何你不完全信任的來源，有人只要塞一個 `"; rm -rf ~"` 進去，就能讓你的程式執行任意指令——這就是**命令注入（command injection）**，OWASP 十大風險之一，不是理論上的風險,是真實會被利用的漏洞類型。

用 list 形式 `["git", "log", branch]`，`branch` 永遠只會被當成**一個參數的值**，不管它裡面寫了什麼符號，都不會被 shell 重新解析。這也是為什麼規格明確禁止 `shell=True`——不是風格偏好，是消除一整類漏洞。

## `capture_output=True, text=True` 在幫你做什麼

`capture_output=True` 把子行程的 stdout/stderr 接住存成 `result.stdout`/`result.stderr`，不會直接印到你的終端機——這樣你的程式可以自己決定要不要顯示、要怎麼解析這些輸出，而不是讓子行程的輸出跟你自己的輸出混在一起。`text=True` 讓這些輸出自動變成字串（不加的話你拿到的是 bytes，還要自己 `.decode()`）。

## `git status --porcelain` 為什麼比不加參數的 `git status` 適合給程式解析

不加參數的 `git status` 輸出是設計給人看的：有顏色、有提示文字、格式可能隨 git 版本改變。`--porcelain` 是 git 明確承諾「這個格式穩定、專門給腳本解析用」的輸出模式——這是個通用原則：**很多 CLI 工具會分別提供「給人看」跟「給程式解析」兩種輸出格式**（呼應 day07 提到的 `--json`），呼叫外部工具前，先查它有沒有提供這種穩定格式，不要直接解析給人看的輸出，那種格式沒有向後相容的保證。

## 一個發生在這個訓練專案裡的真實案例：呼叫「會自己跳過安全檢查的子行程」

你在幫 `gate.py` 加 `--review` 功能時，設計是讓 `gate.py` 用 `subprocess.run(["claude", "-p", prompt, "--permission-mode", "bypassPermissions"], ...)` 去呼叫另一個 AI agent 幫你評分。這段程式碼本身沒有 `shell=True`，是安全的 list 形式——但它被 Claude Code 自己的自動安全分類器擋下來了，**因為它做的事情是「產生一個關掉所有權限確認的子行程」，這正是 day09 這個主題的極端版本：你不只是呼叫外部程式，你是在呼叫一個「被你明確要求跳過信任邊界檢查」的外部程式。**

這給你一個具體的判斷框架，之後看到任何 `subprocess.run(...)` 呼叫外部程式時都可以問：**這個子行程拿到的權限跟能力,跟呼叫它的程式一樣大嗎？如果子行程本身也會執行使用者輸入、寫檔案、發網路請求，你是在把信任邊界往外推一層,還是在複製一份風險？** `gate.py` 的 `run_pytest()` 呼叫 `pytest` 是相對低風險的（唯讀、跑在你自己的專案目錄），跟呼叫一個權限全開的 AI agent 完全不是同一個風險等級,即使兩者都只是一行 `subprocess.run()`。

## `monkeypatch` 測試外部依賴：不要在測試裡真的呼叫 git

規格要求用 `monkeypatch`（pytest 提供的、暫時替換函式或物件的機制）模擬 `subprocess`，理由很直接：**你的測試不應該依賴外部環境的狀態**（例如當前目錄是不是 git repo、有沒有安裝 git、有沒有網路）。如果測試真的呼叫 `subprocess.run(["git", ...])`，換一台沒裝 git 的機器、或在 CI 環境的乾淨容器裡，測試就會無緣無故失敗——這種失敗跟你的程式邏輯完全無關,卻會讓人誤以為程式壞了。用 `monkeypatch` 讓 `subprocess.run` 回傳你指定的假結果（例如假裝 `git branch --show-current` 回傳 `"main"`），測試就只驗證「拿到這個輸出後，我的程式怎麼處理」，跟「git 到底裝了沒」完全脫鉤。
