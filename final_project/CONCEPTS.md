# 延伸知識：從「能跑的工具」到「可以發行給別人用的工具」還差什麼

## `pyproject.toml` 在解決什麼問題

`final_project/pyproject.toml` 是現代 Python 套件的標準設定檔，取代了舊式的 `setup.py`。它宣告這個套件叫什麼名字、依賴什麼、Python 版本要求是什麼——**有了它，別人（或另一台機器）才能用 `pip install .` 或 `pip install -e .`（editable install，開發模式安裝）把你的工具裝成一個真正的套件，而不是永遠只能在這個特定目錄下用 `python -m price_report` 執行。** 這是「你自己專案目錄下能跑的腳本」跟「可以發行、可以被其他專案依賴的套件」之間的分界線。

## `console_scripts`／entry point：`pip install` 之後為什麼會多一個指令

如果 `pyproject.toml` 裡宣告了 entry point（進入點），例如：

```toml
[project.scripts]
price-report = "price_report.cli:main"
```

`pip install` 這個套件之後，系統會多一個可以直接打的指令 `price-report`，不需要再打 `python -m price_report`。這就是為什麼你平常在終端機打 `pytest`、`black`、`ruff` 這些指令能直接執行——它們都是透過這種機制安裝的。**這個訓練專案沒有要求你設定 entry point，但知道這個機制存在，你才能看懂任何一個真實的 Python CLI 工具是怎麼從「一段程式碼」變成「終端機裡可以直接打的指令」。**

## `[project.optional-dependencies]`：同一個套件，為什麼有時要分好幾種安裝方式

`requirements-dev.txt` 裡的 `pytest`/`ruff`/`mypy` 是「開發這個工具時才需要」的依賴，跟「執行這個工具本身需要什麼」是兩件事。真實世界的 `pyproject.toml` 常常會把依賴拆成好幾組：

```toml
[project]
dependencies = ["some-core-lib"]     # 一定要裝，工具才能跑

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]      # 開發者才需要
gpu = ["some-gpu-backend"]            # 只有想用 GPU 加速的人才需要
```

安裝時可以用 `pip install .[dev]`、`pip install .[gpu]` 選擇性地多裝某一組——**不是每個使用這個套件的人都需要開發工具，也不是每個人都有 GPU 環境去裝 GPU 相關的依賴**，硬把所有東西塞進同一份必裝清單，會讓一個只想單純執行工具的人被迫裝一堆自己用不到的東西（甚至可能因為某個依賴在他的機器上裝不起來，導致他根本裝不了這個套件）。當你看到一個專案有好幾份 `pyproject*.toml`（例如針對不同硬體後端、不同執行環境各一份），背後的動機通常也是同一件事：**不同使用情境需要的依賴差異太大，乾脆拆成完全獨立的設定檔，而不是硬塞進 optional-dependencies 的分組裡。** 這個訓練專案的依賴很單純（只有 pytest/ruff/mypy），用不到這個機制，但看到 AI 生成的 `pyproject.toml` 裡有 `[project.optional-dependencies]`，現在你知道那是在解決「不同的人、不同情境，需要的東西不一樣」這個問題，不是無意義的複雜化。

## `examples/`、`tests/`、`price_report/` 分開放，這個目錄結構在說什麼

`final_project` 底下的 `examples/`（範例輸入檔）、`tests/`（測試）、實際套件程式碼各自獨立成資料夾，這是業界常見的 Python 專案佈局：**套件本身的程式碼跟「用來示範、測試這個套件」的東西分開放，讓人一眼就知道哪些是「產品」、哪些是「輔助材料」。** 這跟 day13 談的模組內部職責分離是同一個精神，只是拉高到整個專案的檔案佈局層級。

## `sys.path`：`python -m price_report` 幫你避開了什麼

Python 執行 `import price_report.cli` 這種語句時，會去一個叫 `sys.path`（一個字串 list，內容是「Python 找模組時會搜尋的目錄清單」）裡列出的每個目錄，找有沒有一個叫 `price_report` 的資料夾或檔案。`sys.path` 的內容不是固定的，其中一項規則是：**用 `python -m 某模組名稱` 執行時，Python 會把「執行時所在的目前目錄」自動加進 `sys.path`。** 這就是為什麼你要先 `cd final_project`、再跑 `python -m price_report ...`——這樣 `sys.path` 裡才會有 `final_project/`，Python 才能在裡面找到 `price_report/` 這個套件目錄。

如果你換一種跑法，直接 `cd final_project/price_report` 再 `python cli.py`，會撞到 `ModuleNotFoundError: No module named 'price_report'`——因為這時候「目前目錄」是 `price_report/` 這一層，`sys.path` 裡完全沒有 `final_project/`，Python 找不到那個套件名稱。這正是新手（以及很多 AI 生成的範例程式碼）最常卡住、也最常見的「明明程式碼沒寫錯，卻 import 不到」的情境——問題通常不在程式碼本身，而在**從哪個目錄、用哪種方式執行**。

## 撞到 `ModuleNotFoundError` 時，實務上有哪幾種解法（以及它們的差別）

1. **換執行方式**（這天用的方法）：改用 `python -m 套件名稱`，從套件的上一層目錄執行，讓 Python 自動把正確的目錄加進 `sys.path`。這是最乾淨的解法，因為你完全不用手動碰 `sys.path`。
2. **手動塞路徑**：在程式碼最上面寫 `import sys; sys.path.insert(0, "某個目錄")`，強迫把那個目錄加進搜尋清單。這是 AI 生成程式碼裡很常見的「急救」寫法——**它能讓程式跑起來，但通常代表專案的目錄結構或執行方式有問題，是在掩蓋根本原因，不是在解決它**。而且這種寫法裡的路徑常常是寫死的絕對路徑或用 `../..` 硬湊的相對路徑，換一台機器、換一個執行目錄就會壞。看到 AI 建議在程式碼裡加 `sys.path.insert/append`，值得先問自己「是不是應該換成 `-m` 或安裝成套件，而不是修 `sys.path`」。
3. **`PYTHONPATH` 環境變數**：執行前設定 `PYTHONPATH=/某路徑`（例如 `PYTHONPATH=. python 某腳本.py`），效果類似手動塞路徑，但不用改程式碼本身。常見於 CI（Continuous Integration，自動化測試流程）設定或暫時除錯，不是長期解法。
4. **真正安裝成套件**：像前面談的 `pip install -e .`——裝完之後 `price_report` 對 Python 來說就是一個「正式安裝過的套件」，不管你在哪個目錄下執行 `python`，都找得到它，完全不需要處理 `sys.path`。這才是給別人用、或要長期維護的工具該走的路。

## 相對匯入（relative import）跟絕對匯入（absolute import）

`__main__.py` 裡寫的 `from price_report.cli import main` 是絕對匯入——完整寫出套件路徑，從 `sys.path` 裡的某個根目錄開始找。你也可能在其他專案的原始碼裡看到套件內部模組互相參照時寫成 `from .cli import main`（開頭的 `.` 代表「同一個套件裡」）——這是相對匯入，只能在套件內部使用，不能拿來執行單一檔案（`python cli.py` 這種直接執行的方式看不到「套件」這個概念，會直接報錯）。這個專案的模組全部用絕對匯入（`from price_report.xxx import yyy`），是刻意選擇的——**絕對匯入在檔案被移動、或被其他工具匯入時行為比較好預測，也是目前業界比較常見的建議寫法**；但看到別的專案用 `.` 開頭的相對匯入時，你現在知道那是什麼、為什麼只能配合套件執行方式使用。

## 一份結構化資料流過七個模組，誰能改它、誰不能

`parser.py` 解析出一批 `PriceRecord`（day10 的 frozen dataclass），接著這批資料會依序流進 `scoring.py`、`report.py`。這是這整個訓練裡「複雜資料結構跨函式/跨模組傳遞」規模最大的一次，值得把 day01、day10 講過的別名（aliasing）風險放到這個尺度重新想一次：

- `scoring.py` 拿到的那個 `list[PriceRecord]`，跟 `parser.py` 手上的是**同一個 list 物件**，不是複製品。如果 `scoring.py` 對它 `.sort()`、`.append()`，`parser.py`（或任何其他還握著這份資料的模組）看到的順序也會被悄悄改變。
- 因為 `PriceRecord` 是 `frozen=True` 且欄位全是不可變型別（day10 提過的細節），**你不需要擔心裡面每一筆資料被就地修改**——真正該留意的只剩「裝這些資料的最外層 list 本身」有沒有被意外排序或增刪。實務上的解法很簡單：`scoring.py` 需要排序時，用 `sorted(results)` 產生新 list，不要對傳進來的參數呼叫 `.sort()`。
- 把這個原則講清楚一點：**跨模組邊界傳遞的資料，預設當作唯讀**。一個模組如果需要「基於輸入算出新東西」，該回傳一個新的結構（新的 list、新的 dict、新的 dataclass），而不是就地修改傳進來的參數再回傳 `None`——這樣呼叫端才能放心，呼叫完之後手上的原始資料還是原來那份，不需要每次呼叫前都先自己複製一份防禦性拷貝。

## 一個經典地雷：mutable default argument

跟「傳遞」相關、AI 生成程式碼裡真實會出現的另一個地雷，是函式參數給了 mutable（可變）的預設值：

```python
def build_report(store_list, extra_notes: list[str] = []):   # 地雷
    extra_notes.append("generated")
    ...
```

`extra_notes=[]` 這個空 list 只在函式**定義的時候**建立一次，不是每次呼叫都重新建立一個新的空 list——所有沒有明確傳入 `extra_notes` 的呼叫，共用的是**同一個** list 物件。第一次呼叫把 `"generated"` 塞進去之後，這個 list 就永久多了一個元素，下一次沒帶參數呼叫這個函式時，會發現 `extra_notes` 裡莫名其妙已經有東西了——而且這個 bug 只有呼叫兩次以上才會現形，寫測試時很容易漏。正確寫法是預設值給 `None`，函式內部再判斷：

```python
def build_report(store_list, extra_notes: list[str] | None = None):
    extra_notes = extra_notes if extra_notes is not None else []
    ...
```

這個地雷幾乎每個 Python 開發者都踩過一次，包括 AI 生成的程式碼——看到函式簽名裡的預設值是 `[]`、`{}`，或任何看起來是「空容器」的寫法，值得停下來確認一次。

## 這整套訓練走到這裡，跟「讓 AI 幫你生成一個完整工具」的差距在哪

如果你從第一天就直接跟 AI 說「幫我寫一個價格報表工具」，AI 很可能可以一次生成出跟 `final_project` 結構相似、甚至更完整的程式碼——**這不是這套訓練想否定的事,AI 確實能做到這件事。這套訓練想確保的是:當那份程式碼生成出來之後,你有沒有能力回答「這裡為什麼要幾何平均不用算術平均」「這個 exit code 為什麼是 5 不是 3」「這個模組為什麼不該 import argparse」——如果答不出來，你手上的是一個你不完全理解、也就無法安全修改的黑箱，不管它現在能不能跑。** 這就是全域規格從第一天就寫的那句話的意思：AI 是加速器，不是答案來源。
