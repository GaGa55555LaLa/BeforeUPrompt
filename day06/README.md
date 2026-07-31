# Day 06：完整測試 Day 05

將 Day 05 程式複製並改善可測試性。

## 必測案例
正常、空檔、只有 header、單筆、負數、0、NaN、缺欄位、非數字、baseline 不存在、重複項、名稱含前後空白。

對名稱空白必須選擇：自動 strip、視為不同名稱、或視為錯誤；記錄理由。

## 必用
```python
with pytest.raises(ValueError):
    ...
```
至少一次使用 `tmp_path`。

## 驗收
`pytest -v` 全部通過，至少 12 個測試。

## 口頭驗收
測試是在驗證外部行為，還是綁死內部實作？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
