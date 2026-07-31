# Day 19（延伸）：asyncio 基礎

本日為選修延伸，不計入兩週核心天數。銜接 day05 的價格計算與 day09 的 subprocess，主題是「同時等待多件事，而不是一件一件排隊等」。

## 情境

模擬同時查詢多間商店的商品價格。每次查詢都要「等待」一段時間（模擬真實世界裡等待對方系統回應、或等待網路回應），如果一間一間依序等，總耗時是所有等待時間相加；這天要用 `asyncio` 讓所有查詢同時進行，總耗時接近「最長的那一個」，不是總和。

## 必做功能

```python
async def check_price(store: str, price: float, delay: float) -> tuple[str, float]:
    """delay < 0 視為不合法輸入，應拋出 ValueError。"""

async def check_all(jobs: list[tuple[str, float, float]]) -> dict[str, float]:
    """jobs 是 (store, price, delay) 的 list，用 asyncio.gather 同時執行，
    回傳 {store: price} 的 dict。任何一個 check_price 失敗，整體立即拋出該例外。"""
```

- `check_price` 內部**必須**用 `await asyncio.sleep(delay)` 模擬等待，**不得**用 `time.sleep(delay)`——這是這天故意要踩一次的地雷（見 `CONCEPTS.md`）。
- `check_all` 用 `asyncio.gather()`，同時發起所有查詢。
- `jobs` 為空 list 時回傳空 dict，不得卡住或報錯。

## 執行
```bash
python solution.py "S01:1.0:0.2" "S02:8.7:0.1" "S03:12.0:0.15"
```
（`store:price:delay` 用冒號分隔，內部呼叫 `check_all` 並輸出 JSON。）

## 測試
至少 5 個，須包含：多個 job 同時執行、總耗時明顯小於「各 delay 相加」（用 `time.monotonic()` 前後量測，門檻值留足夠寬裕避免環境快慢造成誤判）、遇到不合法 delay 時整體拋出例外、空 job list、`delay=0` 是否合法（自行決定並測試該行為）。

## 口頭驗收
三個各等待 0.2 秒的查詢，`check_all` 總共花多久？如果 `check_price` 內部誤用 `time.sleep()` 而不是 `await asyncio.sleep()`，結果會有什麼不同（提示：程式仍然「能跑」，但失去了什麼）？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）——裡面額外講了 `asyncio.gather(..., return_exceptions=True)` 這個變化，不強制實作，有興趣可以自己再多寫一版。
