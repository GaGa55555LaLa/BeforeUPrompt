# Day 17（延伸）：物件導向與 Context Manager

本日為選修延伸，不計入原本兩週的 14 天核心範圍，銜接 day10 的 dataclass 與 day12 的資源錯誤處理。

## 目標
練習一般 class（有方法、有內部狀態，跟 day10 只裝資料的 `frozen dataclass`不同）與 context manager（`with` 陳述式背後的協定）。

## 必做功能一：`PriceTracker`

一般 class（**不得**用 `@dataclass`），維護一組商店價格：

```python
class PriceTracker:
    def __init__(self) -> None: ...
    def add(self, store: str, price: float) -> None: ...
    def average(self, store: str) -> float: ...
    def to_dict(self) -> dict[str, float]: ...
```

- `add`：`store` 為空字串應拋 `ValueError`；`price` 為負數、NaN、Infinity 應拋 `ValueError`。
- `average`：對不存在的 `store` 應拋 `KeyError`；同一 `store` 有多筆價格時回傳算術平均。
- `to_dict`：回傳「每個商店 → 平均價格」的 dict，內部須用 dict comprehension（生成式）實作，不得手寫迴圈 `+ append`/`+= ` 累加後再轉換。

## 必做功能二：計時 context manager（兩種寫法都要做）

```python
class Timer:
    def __init__(self, label: str) -> None: ...
    def __enter__(self) -> "Timer": ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None: ...
    # 結束後可讀 self.elapsed（秒）

from contextlib import contextmanager

@contextmanager
def timer(label: str):
    ...  # 用 yield 實作，行為必須跟 Timer 等價
```

- 不論 `with` 區塊內是否拋出例外，離開時都必須把耗時記下來（可記到一個模組層級的 list，供測試檢查）。
- `__exit__` 不得吞掉例外——區塊內的例外必須照常往外傳播。

## 規則
- `PriceTracker`、`Timer` 皆為一般 class；公開方法有型別標註。
- 不使用 `time.sleep` 之外的方式人工延遲；測試不依賴真實耗時數值，只驗證「有沒有被記錄」與「例外有沒有正常傳播」。

## 測試
至少 8 個，須包含：正常新增與計算平均、空 tracker 查詢不存在商店、`add` 拒絕不合法輸入、`to_dict` 內容正確、`Timer` 正常結束記錄耗時、`Timer` 區塊內拋例外仍記錄耗時且例外正常往外傳、兩種 context manager 寫法行為一致、對同一商店重複 `add` 後平均值正確更新（容易忽略案例）。

## 口頭驗收
`PriceTracker` 跟 day10 的 `frozen dataclass` 該怎麼選？如果 `__exit__` 回傳 `True` 會發生什麼事？為什麼這天要求 class 版跟 `contextlib.contextmanager` 版都寫一次？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
