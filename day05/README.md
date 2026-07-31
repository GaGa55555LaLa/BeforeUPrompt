# Day 05：CSV 價格統計

## 執行
```bash
python solution.py prices.csv --baseline S01
```

## CSV
```csv
store,item,price
S01,rice,1.0
S01,milk,1.0
S02,rice,12.4
S02,milk,8.7
```

## 每個商店輸出
測項數、算術平均、幾何平均、相對 baseline 的幾何平均倍率。

## 驗證
- 欄位必須完整。
- store/item 非空。
- price 為有限正數；拒絕 0、負數、NaN、Infinity。
- baseline 必須存在。
- store + item 不得重複。

## 限制
使用 `csv.DictReader`；解析、計算、輸出分離。

## 測試
至少 10 個。

## 口頭驗收
為何幾何平均不能接受負數？倍率資料何時適合幾何平均？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
