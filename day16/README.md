# Day 16（延伸）：程式碼品質工具與可維護測試

本日為選修延伸，不計入原本兩週的 14 天核心範圍，銜接 day06/day12 的測試案例覆蓋與 day11 的重構。

## 執行
```bash
python solution.py data.csv --column price
```

## CSV
```csv
store,item,price
S01,rice,1.0
S01,milk,
S02,rice,12.4
S02,milk,8.7
```

## 功能
針對指定欄位輸出：`count`（可轉成數字的筆數）、`missing`（空字串或缺欄位的筆數）、`min`、`max`、`mean`。

## 驗證
- 欄位不存在（不在 header 裡）：報錯，訊息需指出欄位名稱。
- 欄位存在但全部是空值或非數字：報錯。
- 空字串視為缺值（`missing`），不計入 `count`／`min`／`max`／`mean`。
- 非數字、非空字串（例如 `"abc"`）：報錯，訊息需指出是哪一列出的問題。

## 規則一：靜態檢查工具過關

安裝 `requirements-dev.txt` 後執行：

```bash
ruff check solution.py
mypy solution.py
```

兩者皆須 0 錯誤。`ruff`（linter，靜態分析程式碼風格與常見錯誤模式，不執行程式碼）跟 `mypy`（static type checker，依你寫的型別標註做靜態型別檢查）都是開發工具，不是 `solution.py` 執行時會 `import` 的第三方套件，跟 `SPEC.md` 「不得依賴第三方套件」的限制不衝突（跟 `pytest` 是同一類例外）。`notes.md` 需記錄：跑第一次遇到什麼被抓出來的問題（若一次就過關，寫下你在寫的時候做了什麼讓自己避開了常見的那幾種）。

## 規則二：`conftest.py` 與 `parametrize`

- 建立 `conftest.py`，至少提供一個 fixture（例如 `sample_csv(tmp_path)`，回傳一個已寫好內容的臨時 CSV 檔路徑），供多個測試函式共用，不得在每個測試函式裡各自重複寫建立臨時檔案的程式碼。
- 用 `@pytest.mark.parametrize` 覆蓋至少 6 組案例：正常欄位、欄位不存在、欄位含缺值、欄位全空、含非數字值、單列 CSV（容易忽略案例）。

## 測試
至少 8 個（含上述 parametrize 組合），涵蓋 CLI 呼叫層跟計算層。

## 口頭驗收
`conftest.py` 裡的 fixture 跟你自己在每個測試裡複製貼上準備資料的程式碼，差在哪？這次的案例裡有沒有哪一種其實不該塞進同一個 `parametrize`？`ruff` 跟 `mypy` 各自在檢查什麼，能不能互相取代？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
