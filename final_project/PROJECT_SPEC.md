# Store Price Index Reporter 完整規格

## 1. CLI

```bash
python -m price_report --results PATH --config PATH --output PATH [--verbose]
```

| 參數 | 必填 | 說明 |
|---|---:|---|
| `--results` | 是 | CSV 結果檔 |
| `--config` | 是 | TOML 設定檔 |
| `--output` | 是 | JSON 報告路徑 |
| `--verbose` | 否 | 顯示 DEBUG 級別紀錄 |

## 2. TOML

```toml
[tracking]
baseline = "S01"
min_coverage = 0.5
required_items = ["rice", "milk", "eggs"]

[output]
indent = 2
```

驗證：

- baseline：非空字串。
- min_coverage：0.0～1.0，包含邊界。
- required_items：至少一項；各項非空；不得重複。
- indent：整數 0～8。

## 3. CSV

```csv
store,item,price,priced
S01,rice,1.0,true
S01,milk,1.0,true
S01,eggs,1.0,true
S02,rice,18.2,true
S02,milk,17.4,true
S02,eggs,0,false
```

驗證：

- 四個欄位皆存在。
- store/item 去除前後空白後不得為空。
- item 必須在 required_items。
- priced 只接受不分大小寫的 `true`、`false`。
- priced=true：price 為有限正數。
- priced=false：price 必須為 0。
- store + item 不得重複。
- baseline 必須存在，且 required_items 全部 priced。

## 4. 計算

### Coverage

```text
已 priced 的 required item 數 / required_items 總數
```

### Price Basis

- coverage = 1.0：`Priced`
- min_coverage <= coverage < 1.0：`Estimated`
- coverage < min_coverage：`Invalid`

### 分數（價格指數）

- 只使用 priced=true 的 price 計算幾何平均。
- 相對倍率 = 該店幾何平均 / baseline 幾何平均（等同該店與 baseline 逐項價格比的幾何平均，即 Jevons price index 的算法）。
- Invalid 的 `relative_to_baseline` 必須為 `null`。
- 本作業不實作真正缺項推估；`Estimated` 只代表資料不完整但 coverage 達標。

## 5. JSON

```json
{
  "baseline": "S01",
  "required_items": ["rice", "milk", "eggs"],
  "stores": [
    {
      "name": "S01",
      "priced_items": 3,
      "total_items": 3,
      "coverage": 1.0,
      "price_basis": "Priced",
      "geometric_mean": 1.0,
      "relative_to_baseline": 1.0
    }
  ]
}
```

要求：

- stores 依名稱排序。
- 浮點數維持 JSON number，不轉成字串。
- UTF-8。
- 自動建立輸出父目錄。
- 不得輸出 NaN 或 Infinity。

## 6. Exit code

| 狀況 | Code |
|---|---:|
| 成功 | 0 |
| CLI 參數錯誤 | 2（argparse） |
| 輸入檔不存在 | 3 |
| TOML 錯誤 | 4 |
| CSV 錯誤 | 5 |
| 計算錯誤 | 6 |
| 輸出失敗 | 7 |
| 未預期錯誤 | 10 |

## 7. Logging

- 預設 INFO。
- `--verbose` 時 DEBUG。
- 一般結果到 stdout，錯誤到 stderr。

## 8. 最低測試

至少 15 個，涵蓋：完整資料、Estimated、Invalid、coverage 恰好門檻、baseline 缺失或不完整、CSV 缺欄位、重複、NaN/Infinity、false 但 price 非 0、未知 item、TOML 錯誤、輸出失敗、排序及 CLI exit code。

## 9. 例外類別

- 定義自己的例外類別，至少：`ConfigError`（TOML 相關）、`CsvError`（CSV 相關）、`ScoringError`（計算相關）、`OutputError`（輸出相關），全部繼承自共同的基底類別（例如 `PriceReportError(Exception)`）。
- `config.py`／`parser.py`／`scoring.py`／`report.py` 各自只拋出自己負責的例外類別，不得互相拋對方的類別。
- `cli.py` 依例外**型別**（不是解析錯誤訊息字串）對應到第 6 節的 exit code；`except PriceReportError` 這種捕捉共同基底類別的寫法，不得用來取代逐一對應個別 exit code。

## 10. 結構要求

- 公開函式有型別標註。
- 模組責任清楚。
- 不使用全域可變狀態。
- 不依賴 pandas、NumPy。
- 測試不依賴網路。
