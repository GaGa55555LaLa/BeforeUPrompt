# Day 18（延伸）：抽象基底類別與介面設計

本日為選修延伸，不計入兩週核心天數。銜接 day17 的一般 class，主題是「一個介面，多種實作」——這是真實專案裡最常見的物件導向設計模式之一。

## 情境

價格資料可能來自不同來源（先寫死在程式裡的固定資料、CSV 檔案，未來也許還會有 API），但呼叫端（例如算總價的函式）不該關心資料到底從哪來,只該關心「給我商品名稱,回我價格」這個共同介面。

## 必做功能

```python
from abc import ABC, abstractmethod

class PriceSource(ABC):
    @abstractmethod
    def fetch_price(self, item: str) -> float:
        """回傳指定商品的價格；查不到時應拋 KeyError。"""

class StaticPriceSource(PriceSource):
    def __init__(self, prices: dict[str, float]) -> None: ...
    def fetch_price(self, item: str) -> float: ...

class CsvPriceSource(PriceSource):
    def __init__(self, path: Path) -> None: ...
    def fetch_price(self, item: str) -> float: ...

def total_price(source: PriceSource, items: list[str]) -> float:
    """對每個 item 呼叫 source.fetch_price 並加總。items 為空時回傳 0.0。"""
```

## 規則
- `PriceSource` 必須是 `ABC`，`fetch_price` 必須是 `@abstractmethod`。
- `StaticPriceSource`、`CsvPriceSource` 都繼承 `PriceSource`，簽名一致（同名方法、同樣的參數與回傳型別）。
- `total_price()` 的參數型別標註必須寫成 `PriceSource`（抽象型別），**不得**寫成某個具體子類別；函式內部也不得用 `isinstance` 去判斷「這是哪一種 source」再分別處理。
- `CsvPriceSource` 讀取的 CSV 至少有 `item,price` 兩欄。

## 測試
至少 6 個，須包含：直接 `PriceSource()` 實例化應拋 `TypeError`（抽象方法未實作不能建立實例）、`StaticPriceSource` 正常查價、`CsvPriceSource` 正常查價（用 `tmp_path` 建臨時 CSV）、兩者查不到商品都拋 `KeyError`、`total_price()` 對兩種 source 傳入同一組 `items` 得到一致行為（重點在證明函式不用知道具體類別）、`items` 為空時回傳 `0.0`。

## 口頭驗收
`total_price()` 的型別標註寫成 `PriceSource` 而不是某個具體子類別，換來什麼好處？如果之後要加第三種 `ApiPriceSource`，`total_price()` 需要改嗎？`@abstractmethod` 沒有被子類別實作會發生什麼事？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
