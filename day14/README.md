# Day 14：期末專案完成與獨立驗收

## 完成項目
CLI、TOML/CSV 驗證、dataclass、coverage、Price Basis、相對 baseline 倍率、JSON、logging、exit code、`--help`、README、至少 15 個測試。

## 最終驗收
```bash
cd final_project
python -m price_report --results examples/results.csv --config examples/config.toml --output report.json
pytest -v
```

## 30 分鐘獨立題
建立 `independent_challenge.py`，禁止使用 AI：讀 CSV，按 store 分組，計算 price 算術平均並輸出 JSON；拒絕空名稱、非數字與空資料。至少 3 函式、型別標註、5 個測試。

## 口試
說明入口、資料流、pure function、baseline 缺失位置、新增欄位修改點、三種高風險輸入、測試錯誤案例的原因、AI 協助部分與驗證方式。

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
