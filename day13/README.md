# Day 13：期末專案第一部分

在根目錄 `final_project/` 實作 Store Price Index Reporter。

## 執行
```bash
python -m price_report --results results.csv --config config.toml --output report.json
```

## 今日範圍
套件入口、TOML 驗證、CSV 解析、資料模型、coverage、baseline 驗證、初步 JSON、至少 8 個測試。

## 模組責任
- `__main__.py`：`python -m` 入口。
- `cli.py`：argparse 與 exit code；依例外型別對應 exit code（見 `PROJECT_SPEC.md` 第 9 節）。
- `config.py`：TOML；驗證失敗拋自訂的 `ConfigError`。
- `models.py`：dataclass / enum。
- `parser.py`：CSV；驗證失敗拋自訂的 `CsvError`。
- `scoring.py`：coverage 與倍率；計算失敗拋自訂的 `ScoringError`。
- `report.py`：JSON；輸出失敗拋自訂的 `OutputError`。

## 驗收
```bash
cd final_project
python -m price_report --help
pytest -v
```

## 口頭驗收
CSV 依序通過哪些模組？哪些模組不應知道 argparse？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
