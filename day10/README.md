# Day 10：Dataclass Price Model

## 模型
```python
@dataclass(frozen=True)
class PriceRecord:
    store: str
    item: str
    price: float
    priced: bool
```

## CSV
```csv
store,item,price,priced
S01,rice,1.0,true
S03,rice,18.2,true
S03,milk,0,false
```

## 規則
- priced=true：price 為有限正數。
- priced=false：price 必須為 0。
- coverage = priced item 數 / 全部 item 數。
- coverage=1：Priced。
- 門檻<=coverage<1：Estimated。
- coverage<門檻：Invalid。
- 預設門檻 0.5。

## 輸出
將每個商店摘要轉成 dictionary，再輸出 JSON。

## 限制
解析、計算、輸出分離；不得全用巢狀 dictionary 取代資料模型。

## 測試
至少 10 個。

## 口頭驗收
`frozen=True` 的作用？coverage 恰好 0.5 如何判定？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
