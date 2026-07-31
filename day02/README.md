# Day 02：檔案搜尋工具

## 執行
```bash
python solution.py <directory> <extension>
```
例如 `python solution.py ./sample_project .py`。

## 功能
- 使用 `pathlib.Path`。
- 遞迴尋找指定副檔名。
- 顯示相對路徑與 bytes。
- 按大小由大到小；同大小按路徑排序。
- 無結果時正常結束。

## 錯誤
目錄不存在、輸入不是目錄。副檔名未以 `.` 開頭時，可自動補上或拒絕，但需在 `notes.md` 說明。

## 限制
不得使用 `os.walk()`；不得硬編碼路徑分隔符。

## 測試
至少 6 個，使用 pytest 的 `tmp_path`（臨時目錄）。

## 口頭驗收
`glob()` 與 `rglob()` 差在哪裡？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
