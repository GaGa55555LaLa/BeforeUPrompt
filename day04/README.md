# Day 04：例外處理與 Logging

延續 Day 03，加入 `logging`（程式事件紀錄）及 exit code（程式結束狀態碼）。

## 功能
- INFO 與 ERROR 寫入 `app.log`。
- 錯誤同時輸出到 stderr（標準錯誤輸出）。
- 禁止用 `print()` 寫 log。

## Exit code
| 狀況 | Code |
|---|---:|
| 成功 | 0 |
| 檔案不存在 | 2 |
| TOML 格式錯誤 | 3 |
| 設定不合法 | 4 |
| 輸出失敗 | 5 |

## 限制
禁止 `except Exception: pass`。若最外層捕捉廣泛例外，必須記錄原因。

## 測試
至少 8 個，至少驗證兩種 exit code。

## 口頭驗收
stdout 與 stderr 差在哪？為何要區分 exit code？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
