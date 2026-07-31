# Day 07：第一週小專案 config-check

## 執行
```bash
python solution.py config.toml
python solution.py config.toml --json
```

## 設定
```toml
[tracking]
samples = 8
coverage_threshold = 0.5
items = ["rice", "milk", "eggs"]

[output]
directory = "results"
save_raw_data = true
```

## 功能
讀取與驗證 TOML、顯示摘要、`--json` 輸出 JSON、建立目錄、非零 exit code、`--help`。

## 驗證
samples 正整數；threshold 0～1；items 至少一個非空且不重複；directory 非空；save_raw_data 為布林。

## 額外檔案
完成 `PROJECT_README.md`：環境、使用方式、設定欄位、exit code、已知限制。

## 測試
至少 12 個。

## 口頭驗收
新增一個設定欄位需修改哪些地方？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
