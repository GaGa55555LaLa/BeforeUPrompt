# Day 12：故障注入

Fault injection（故障注入，刻意製造異常驗證可靠性）。使用 Day 10 或 11 的工具。

## 必測
CSV 不存在、空檔、只有 header、缺欄位、重複項、baseline 不存在、NaN、Infinity、負數、非法 priced、coverage 恰好 50%、全部未定價、空白商店名、輸出失敗。

輸出權限在不同作業系統不穩定，可 monkeypatch 模擬 `PermissionError`。

## 驗收
- 至少 14 個測試。
- 錯誤指出原因，不只是被捕捉。
- 正常案例未被破壞。

## 口頭驗收
哪些錯誤由 parser 處理？哪些由 CLI 轉成 exit code？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
