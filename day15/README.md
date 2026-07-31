# Day 15（延伸）：`sys.path` 手動操作

本日為選修延伸，不計入兩週核心天數。銜接 `final_project/CONCEPTS.md` 已經講過的 `sys.path`／`ModuleNotFoundError` 概念，這天要實際動手處理一次。

## 情境

`vendor/stringutils.py` 是一個故意放在套件外面的模組（沒有 `__init__.py`，不是 `import vendor.stringutils`，是要讓 `vendor/` 這個目錄本身出現在 `sys.path` 上，再 `import stringutils`）。直接執行以下指令會得到 `ModuleNotFoundError`：

```bash
python -c "import stringutils"
```

這天要寫一支 `solution.py`，在程式碼裡**手動**把 `vendor/` 加進 `sys.path`，讓這個匯入能成功——而且不管從哪個目錄執行都要能動。

## 執行
```bash
python solution.py "S01 " "River Side Mart"
# 預期輸出：
# s01
# river-side-mart
```

從別的目錄執行也必須得到一樣的結果：

```bash
cd /tmp && python /絕對路徑/day15/solution.py "S02"
```

## 必做功能

```python
def ensure_vendor_on_path() -> Path: ...  # 回傳 vendor/ 的絕對路徑
def main(argv: list[str] | None = None) -> int: ...
```

- `ensure_vendor_on_path()` 用 `Path(__file__).resolve().parent / "vendor"` 算出絕對路徑，**不得**用寫死的絕對路徑字串，也**不得**用 `sys.path.append(".")` 這種依賴「目前工作目錄」的寫法（這種寫法只有從特定目錄執行才會動，換個目錄執行就會壞——這是這天要故意避開的反面案例）。
- 呼叫多次不得讓 `sys.path` 裡出現重複的項目（idempotent，操作可以重複執行,結果不會累積副作用）。
- `import stringutils` 必須寫在 `ensure_vendor_on_path()` 呼叫**之後**（匯入時機很重要：`sys.path` 沒設好之前 import 一定會失敗）。
- `main()` 對每個 CLI 參數呼叫 `slugify()` 並各印一行。

## 測試
至少 6 個，須包含：正常匯入並轉換成功、含前後空白與多個空白字元的輸入（呼應 day06 學過的「trailing whitespace」問題）、`ensure_vendor_on_path()` 呼叫兩次後 `sys.path` 沒有重複項目、用 `subprocess.run` 從**跟 `day15/` 完全無關的目錄**執行 `solution.py` 仍能成功（證明路徑計算跟目前工作目錄無關）、沒有任何參數時的行為（空輸入）、直接 `import stringutils`（不透過 `ensure_vendor_on_path`）確實會拋 `ModuleNotFoundError`（證明這個問題本來就存在，不是憑空多寫的測試）。

## 口頭驗收
`sys.path.append(".")` 跟這天要求的寫法差在哪？如果 `import stringutils` 寫在 `ensure_vendor_on_path()` 呼叫之前會發生什麼事？真實世界裡，還有哪些情境會讓人選擇手動操作 `sys.path`，而不是把東西包成一個可以 `pip install` 的套件？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
