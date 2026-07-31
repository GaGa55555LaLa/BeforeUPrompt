# 延伸知識：lint／型別檢查工具在抓什麼，`conftest.py` 怎麼被 pytest 自動找到

## `ruff` 在檢查什麼：它不執行你的程式碼

`ruff check solution.py` 不會真的跑你的程式，它是靜態分析（static analysis，不執行程式、只讀程式碼文字結構去找問題）：找沒用到的 import、沒用到的變數、`except Exception: pass`（跟 `SPEC.md` 明文禁止的那條規則剛好對得上）、`mutable default argument`（`final_project/CONCEPTS.md` 提過的地雷，`def f(x=[])` 這種寫法 `ruff` 有專門的規則會標出來）這類「不用真的跑起來就能看出來的問題」。它抓的是**寫法層級**的問題，不是「這個函式的商業邏輯對不對」。

## `mypy` 在檢查什麼：它只能檢查你寫出來的型別標註是否互相一致

`mypy solution.py` 檢查的是你自己寫的型別標註（`def mean(values: list[float]) -> float`）有沒有互相矛盾——例如你宣告回傳 `float`，但函式裡某條路徑其實 `return None`；或者呼叫某個函式時傳進去的參數型別跟它宣告的參數型別不符。**它的檢查能力完全取決於你標註得多精確**：如果你偷懶把型別標成 `Any`（代表「這裡什麼型別都算過」，等於放棄檢查）或者根本沒寫型別標註，`mypy` 在那個地方就什麼都抓不到——這不是 `mypy` 的漏洞，是它天生的邊界：**它驗證的是「你宣告的型別合約有沒有被遵守」，不是「這段程式邏輯本身對不對」**。這也是為什麼 `SPEC.md` 從第一天就要求公開函式有型別標註：沒有標註，`mypy` 完全派不上用場。

## `ruff` 跟 `mypy` 能互相取代嗎：不能，它們抓的是兩種不同類型的問題

`ruff` 抓的是「寫法上看起來有問題的模式」（不管型別對不對，這段程式碼的**寫法**本身就是常見地雷）；`mypy` 抓的是「型別標註之間是否自相矛盾」（不管寫法好不好看，這裡的**型別合約**有沒有被違反）。兩者常常同時使用、互不重疊——一段程式碼可能完全沒有型別矛盾（`mypy` 通過），但寫法上有明顯地雷（`ruff` 抓到）；反過來也一樣。真實專案的 CI（Continuous Integration，程式碼推上去前自動跑的檢查流程）裡兩個工具幾乎都會一起跑，不是二選一。

## `conftest.py`：pytest 怎麼「自動」找到它，不需要 import

一般 Python 模組要被用到，你得寫 `import xxx`。`conftest.py` 是 pytest 的特例：**pytest 執行測試時，會自動讀取同一個目錄（以及所有上層目錄）裡叫做 `conftest.py` 的檔案，把裡面用 `@pytest.fixture` 定義的東西變成「這個目錄下所有測試檔案都能直接用」的資源，完全不需要在 `test_solution.py` 裡寫任何 `import conftest`**——這是 pytest 刻意設計的「隱性共享」機制，也是很多新手第一次看到別人的測試檔案裡突然冒出一個沒 import 過的參數名稱（例如 `def test_x(sample_csv): ...`）會困惑的原因：**那個參數名稱不是普通的函式參數，是 pytest 依照名稱去 `conftest.py` 裡找到同名 fixture,自動幫你準備好、傳進來的值。**

```python
# conftest.py
import pytest

@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("store,item,price\nS01,rice,1.0\n", encoding="utf-8")
    return path
```

```python
# test_solution.py
def test_reads_price(sample_csv):
    result = summarize(sample_csv, "price")
    assert result["count"] == 1
```

`sample_csv` 這個名字必須跟 fixture 的函式名稱一致，pytest 靠名稱比對去決定要注入哪個 fixture——這是「依名稱注入依賴」的一種具體實踐，你不需要知道這個詞，但知道背後的機制是「靠名稱比對，不是靠 import」，看到陌生的測試檔案時就不會覺得那個參數是憑空冒出來的。

## fixture 跟複製貼上準備程式碼比，差在哪

如果六組 `parametrize` 案例都要用到「一個內容符合某種格式的臨時 CSV 檔」，把建立這個檔案的邏輯複製貼上六次，跟抽成一個 fixture，**執行結果完全一樣**，差別在於：格式需要調整時（例如欄位順序改變），複製貼上六次的版本要改六個地方，容易漏改；fixture 版本只要改一處。這跟 day06 講的 `parametrize` 收斂重複測試函式是同一種精神，只是這次收斂的是「準備測試資料」這個步驟，而不是「驗證邏輯」本身——**兩者可以同時用：fixture 負責準備共用資料，`parametrize` 負責覆蓋多種輸入變化**，不是互斥的兩個選擇。

## fixture 也可以回傳一個函式，不是只能回傳固定資料

`sample_csv` 這個 fixture 回傳的是一份**寫死內容**的檔案路徑——如果十個測試都需要「內容稍微不同」的 CSV（例如欄位值不同、列數不同），寫死內容的 fixture 就不夠用了。這時候常見的做法是讓 fixture 回傳一個**函式**，讓每個測試呼叫這個函式時自己決定細節：

```python
@pytest.fixture
def make_csv(tmp_path):
    def _make(rows: list[str]) -> Path:
        path = tmp_path / "data.csv"
        path.write_text("store,item,price\n" + "\n".join(rows), encoding="utf-8")
        return path
    return _make          # fixture 回傳的是「函式」本身，不是呼叫結果

def test_normal(make_csv):
    path = make_csv(["S01,rice,1.0"])
    ...

def test_missing_value(make_csv):
    path = make_csv(["S01,rice,"])
    ...
```

`make_csv` 這個 fixture 本身只負責「準備好 `tmp_path`、回傳一個懂得怎麼在那裡寫檔案的函式」，實際要寫什麼內容留給每個測試自己決定——**這是「fixture 負責環境、測試負責資料」的分工**，跟前面 `sample_csv` 那種「fixture 連內容都固定好」的寫法比，多了一層彈性，但也多了一層要讀懂的間接性（先看到 `make_csv` 是個 fixture，還要再看它回傳的東西也是個可呼叫的函式）。**這天的 6 組 `parametrize` 案例如果彼此差異不大，直接用固定內容的 fixture 就夠了；只有當差異大到沒辦法用 `parametrize` 的參數表達時，才值得換成這種「fixture 回傳函式」的寫法**——不要為了看起來更進階就無條件升級。

## AI 生成測試常見的問題：fixture 用得太多，或用了 `autouse` 卻沒講清楚

請 AI 幫忙補測試時，有時會拿到一個把所有東西都包成 fixture 的版本，包括只有一個測試會用到的資料——這種情況下 fixture 反而讓人要跳到另一個檔案才看得懂這個測試在測什麼，得不到「減少重複」的好處，卻多了一層要理解的間接性（indirection）。另一個更隱蔽的問題是 `@pytest.fixture(autouse=True)`：這種 fixture 不需要被任何測試函式的參數列出來，會自動套用在同一個檔案（或目錄）裡的每一個測試上——如果 AI 生成的 `conftest.py` 裡有一個 `autouse` fixture 悄悄改變了每個測試的執行環境（例如自動切換工作目錄、自動 monkeypatch 某個全域設定），但你沒注意到它存在，之後某個測試行為異常時,你會很難聯想到「原因藏在一個看不出來有被呼叫的 fixture 裡」。看到 `conftest.py`，值得花時間確認：這裡的每個 fixture 是不是真的有多個測試在用，以及有沒有 `autouse=True` 在悄悄影響所有測試。
