# Day 01：串列統計函式

## 目標
練習 list（串列）、函式拆分、型別標註與邊界條件。

## 輸入
```python
scores = [12.3, 15.8, 11.9, 18.2, 16.4]
```

## 必做功能
實作至少三個函式：
```python
def mean(values: list[float]) -> float: ...
def above_mean(values: list[float]) -> list[float]: ...
def relative_to_mean(values: list[float]) -> list[float]: ...
```
輸出平均、最大、最小、大於平均值項目、各分數相對平均值倍率。

## 規則
- 空串列拋出 `ValueError`。
- 單一元素可正常處理。
- 不得修改原始串列。
- 不使用 NumPy。

## 驗收範例
`[10.0, 20.0, 30.0]` 應得到平均 20、above `[30.0]`、倍率 `[0.5,1.0,1.5]`。

## 測試
至少 5 個。

## 口頭驗收
為什麼空串列不能取平均？函式是否重複計算平均？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
