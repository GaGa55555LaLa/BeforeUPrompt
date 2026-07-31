# 全域作業規格

## 執行環境

- Python 3.11 以上。
- UTF-8 編碼。
- 除 pytest 外，不得依賴第三方套件，除非當日 spec 明確允許。
- 程式須能從該日目錄或期末專案根目錄執行。

## 程式品質

- 主要功能拆成函式。
- 公開函式具型別標註。
- I/O（Input/Output，檔案、終端或外部命令操作）與 pure function（純函式，只依輸入計算結果）盡量分離。
- 不得將所有邏輯塞進單一 `main()`。
- 不得使用 `except Exception: pass`。
- 預期錯誤不得只顯示難懂 traceback（錯誤呼叫堆疊）。

## 每日提交

```text
dayXX/
├── README.md
├── solution.py
├── test_solution.py
├── notes.md
└── ai_usage.md
```

若當日 spec 指定其他檔案，亦須提交。

## 測試要求

至少包含：

- 正常案例。
- 邊界案例。
- 不合法輸入。
- 空輸入。
- 一個容易忽略的案例。

所有測試須能以 `pytest -v` 執行。

## Git 要求

每日至少一個 commit，例如：

```text
day05: implement CSV price statistics
day05: add invalid-price tests
```

## 驗收層次

1. 功能：輸入、輸出符合 spec。
2. 錯誤：不合法輸入有合理處理。
3. 測試：pytest 全部通過。
4. 解釋：能說明資料流與設計。
5. 修改：需求改動時能自行調整，而非整份重新生成。
