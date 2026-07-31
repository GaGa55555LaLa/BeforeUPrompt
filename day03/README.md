# Day 03：TOML 設定與 JSON 輸出

## 執行
```bash
python solution.py config.toml
```

## TOML
```toml
[tracking]
samples = 8
coverage_threshold = 0.5

[output]
directory = "results"
save_raw_data = true
```

## 功能
- 使用 Python 3.11 `tomllib`。
- 驗證區段與欄位。
- `samples` 為正整數。
- threshold 為 0～1。
- directory 為非空字串。
- save_raw_data 為布林值。
- 建立輸出目錄。
- 寫出 `resolved_config.json`。

## 錯誤
檔案不存在、TOML 語法錯誤、欄位缺失、型別錯誤、數值越界。

## 測試
至少 8 個。

## 口頭驗收
TOML 的 `true` 與 `"true"` 差在哪？為何解析成功仍需驗證？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
