# 延伸知識：為什麼真正的工具是一個套件，不是一個檔案

## 從單一 `solution.py` 到多模組套件，實際換到了什麼

前面 12 天的解答幾乎都是一個 `solution.py`。這在小練習裡沒問題，但真實世界的工具很少長這樣——當一個工具同時要處理「讀設定」「解析輸入」「定義資料模型」「計算」「輸出」這麼多職責時，全部塞進一個檔案會讓人很難只看某一段就知道它負責什麼，改一個地方也容易不小心影響到看起來無關的另一段。`price_report` 這天要求你把職責拆進不同模組：

```text
__main__.py   # python -m 的進入點
cli.py        # argparse 與 exit code
config.py     # TOML
models.py     # dataclass / enum
parser.py     # CSV
scoring.py    # coverage 與倍率
report.py     # JSON
```

每個檔名本身就是文件——**看到 `scoring.py` 就知道去那裡找 coverage 怎麼算的，不用打開一個 800 行的檔案從頭找。**

## `models.py` 裡的 `enum`：Price Basis 這三個狀態為什麼不該用普通字串

`PROJECT_SPEC.md` 要求 Price Basis 只能是 `"Priced"`、`"Estimated"`、`"Invalid"` 三個值中的一個。如果你在程式碼裡到處直接寫這三個字串（`if basis == "Priced": ...`），沒有任何東西擋著你打錯成 `"Priecd"`，或是在另一個檔案裡不小心多定義出第四種狀態 `"Unknown"`——這種錯誤 `mypy`、IDE 都幫不上忙，因為對它們來說這些都只是普通字串。

`enum.Enum`（列舉，把一組固定、互斥的可能值收斂成一個型別）解決的正是這個問題：

```python
from enum import Enum

class PriceBasis(Enum):
    PRICED = "Priced"
    ESTIMATED = "Estimated"
    INVALID = "Invalid"
```

好處很具體：全部合法值都集中宣告在一個地方（想知道「這個分類到底有幾種可能」，看這裡就夠了，不用在程式碼裡到處搜字串）；打錯成 `PriceBasis.PRICEE` 會被 `mypy`／IDE 直接標紅，不會等到執行期才發現；`match`／`if` 判斷式漏掉某個分支時，有些型別檢查工具還能幫你抓出「這裡沒有處理到 `INVALID`」這種遺漏。這跟 day10 用 `frozen dataclass` 取代裸 `dict` 是同一種精神——**把「這裡只能是某幾種值」這個限制,從你腦中的假設,變成型別系統會檢查的規則**。

JSON 輸出時要把 `PriceBasis.PRICED` 轉成字串 `"Priced"`（`json.dump` 不知道怎麼序列化一般的 `Enum` 物件，會直接報錯），這天可以在 `report.py` 裡呼叫 `basis.value` 拿到 `"Priced"` 這個字串。如果不想每次都手動呼叫 `.value`，Python 3.11 起也可以用 `enum.StrEnum`（讓列舉值本身就是字串，`str(PriceBasis.PRICED)` 直接等於 `"Priced"`，`json.dump` 也能直接處理）——這天不強制要求用哪一種寫法，但看到 AI 生成的程式碼用 `Enum` 時，值得確認它有沒有處理好「這個列舉值要怎麼變成 JSON 裡的字串」這一步，這是很容易漏掉、卻只有實際跑到輸出那一行才會報錯的地方。

## `python -m price_report` 這個進入點在做什麼

`__main__.py` 是 Python 的慣例：當你用 `python -m 套件名稱` 執行一個套件時，Python 會去找套件裡的 `__main__.py` 當作起點。這跟直接 `python solution.py` 的差別是：**`-m` 是把整個套件當成一個模組載入,套件內部用相對 import（例如 `from .config import load_config`）互相參照的方式才會正確運作**；直接執行單一檔案的話，這種套件內部的相對 import 常常會失敗。這也是為什麼從 day13 開始要用 `python -m price_report ...` 而不是直接跑某個 `.py` 檔案。

## 每個模組各拋自己的例外類別，`cli.py` 才能靠型別對應 exit code

day04 提過自訂例外類別的基本語法（`class ConfigError(Exception): ...`），這天是它真正派上用場的地方。`PROJECT_SPEC.md` 要求 `config.py`／`parser.py`／`scoring.py`／`report.py` 各自定義並拋出自己的例外類別（`ConfigError`／`CsvError`／`ScoringError`／`OutputError`），`cli.py` 靠 `except ConfigError` 這種**型別**判斷去對應第 6 節的 exit code——不是去檢查錯誤訊息字串裡有沒有「TOML」這個詞。

這個設計直接對應到「哪些模組不應該知道 argparse」這個口頭驗收問題的另一半：`config.py` 拋 `ConfigError` 的時候，完全不知道、也不需要知道這個例外最後會變成 exit code 4——它只負責「這裡真的有錯，而且錯誤的種類是設定檔問題」這一件事。**知道「設定檔錯誤該對應 exit code 4」這個決定，只存在於 `cli.py` 一個地方**，這正是 day13 一路強調的模組職責分離,套用到例外處理這一層。如果之後 `PROJECT_SPEC.md` 改成「TOML 錯誤要拆成語法錯誤跟欄位驗證錯誤兩種不同 exit code」，你只需要在 `config.py` 裡多定義一個例外子類別（例如 `TomlSyntaxError(ConfigError)`），再讓 `cli.py` 多加一個 `except`，`config.py` 原本拋 `ConfigError` 的地方完全不用改。

## 為什麼 `cli.py` 不應該知道 `scoring.py` 怎麼算幾何平均，反過來也一樣

這天口頭驗收問「哪些模組不應該知道 argparse」——答案應該是除了 `cli.py`（跟可能的 `__main__.py`）以外，其他模組都不該知道。`scoring.py` 只該關心「給我一堆 `PriceRecord`，我算出 coverage 跟倍率」，它不該知道這些資料是從 CLI 參數、還是從一個 Web API、還是從測試案例直接建構出來的。**這種「下層模組不知道上層怎麼呼叫它」的原則，讓 `scoring.py` 可以完全獨立測試（不用假裝有 CLI 參數），也讓你未來如果想幫這個工具加一個 Web 介面或 GUI，`scoring.py`、`models.py`、`parser.py` 完全不用改，只需要換掉 `cli.py` 那一層。**

## AI 生成程式碼常見的「單一大檔案」傾向，以及為什麼會這樣

如果你直接跟 AI 說「幫我寫一個讀 CSV、算價格指數、輸出 JSON 的工具」，很常見會得到一個從頭到尾的單一檔案——**因為這樣最快滿足「能跑」這個表面目標，AI 沒有主動的動機去預測「這個工具之後會不會需要拆分」，除非你明確要求模組化結構、或者描述了未來可能的擴充方向。** 這正是為什麼「請 AI 寫程式」跟「請 AI 依照你設計好的架構寫程式」是完全不同層次的合作——前者你拿到的是一個能動但結構未知的黑箱，後者你至少事先想清楚了職責邊界在哪裡，AI 只是幫你填空。這天要求你自己先想過模組職責表，再開始寫，就是在練這個「先設計、後實作」的順序，而不是讓實作細節反過來決定架構。
