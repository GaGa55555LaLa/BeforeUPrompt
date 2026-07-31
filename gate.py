"""Daily gate: enforce the 20-minute independent-work timer and collect grading evidence.

Run from inside a dayXX/ (or final_project/) directory:

    python ../gate.py start            # begin the timer, blocks with a countdown
    python ../gate.py status           # check remaining time without blocking
    python ../gate.py finish           # after the timer, run pytest + collect evidence
    python ../gate.py finish --force   # finish early even if the timer hasn't elapsed
                                        # (honestly recorded in the report as an early finish)
    python ../gate.py finish --declare y   # answer the honesty declaration non-interactively
                                            # (still your own honest answer, just given as an
                                            # argument instead of typed at an input() prompt —
                                            # e.g. so a Claude Code command can pass it through)
    python ../gate.py finish --review  # finish 完成後自動呼叫 claude -p 觸發 reviewer 評分
                                    # （需要 claude CLI 在 PATH，且會以
                                    #  --permission-mode bypassPermissions 執行，
                                    #  讓 reviewer 能自行跑 pytest 等唯讀動作）

This script does NOT assign a score. It only verifies what can be verified
mechanically (elapsed time, required files, pytest result, non-empty notes)
and records an honest self-declaration about AI usage. Scoring against
RUBRIC.md is left to a human or an AI agent reading the generated report.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

CWD = Path.cwd()
STATE_FILE = CWD / ".gate_state.json"
REPORT_FILE = CWD / ".gate_report.md"
DEFAULT_MINUTES = 20
DAY_REQUIRED = ["README.md", "solution.py", "test_solution.py", "notes.md", "ai_usage.md"]


def load_state() -> dict:
    if not STATE_FILE.is_file():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def cmd_start(minutes: int, force: bool) -> int:
    state = load_state()
    if state.get("start_time") and not force:
        elapsed = time.time() - state["start_time"]
        remaining = state.get("minutes", DEFAULT_MINUTES) * 60 - elapsed
        if remaining > 0:
            print(f"計時已在進行中，還剩 {int(remaining)} 秒。若要重設請加 --force。")
            return 1
        print("計時已經結束過一次。若要重新開始請加 --force。")
        return 1

    state = {"start_time": time.time(), "minutes": minutes, "declaration": None}
    save_state(state)

    print(f"=== {CWD.name}：獨立實作階段開始，{minutes} 分鐘倒數 ===")
    print("前這段時間禁止讓 AI 寫完整函式或完整答案，只能查官方文件、讀錯誤訊息。")
    print("可以 Ctrl+C 離開倒數畫面，計時仍會依照時間戳記繼續累計，不會重置。\n")

    deadline = state["start_time"] + minutes * 60
    try:
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            mm, ss = divmod(int(remaining), 60)
            print(f"\r剩餘 {mm:02d}:{ss:02d}", end="", flush=True)
            time.sleep(1)
        print("\r時間到，可以進入提示模式（見 AI_POLICY.md 第 2 階段）。      ")
    except KeyboardInterrupt:
        print("\n已離開倒數畫面，計時仍在背景累計，可用 `status` 查詢剩餘時間。")
    return 0


def cmd_status() -> int:
    state = load_state()
    if not state.get("start_time"):
        print("尚未呼叫 start。")
        return 1
    remaining = state["minutes"] * 60 - (time.time() - state["start_time"])
    if remaining > 0:
        mm, ss = divmod(int(remaining), 60)
        print(f"還剩 {mm:02d}:{ss:02d}")
    else:
        print("時間已到，可以呼叫 finish。")
    return 0


def check_required_files() -> list[str]:
    required = DAY_REQUIRED if (CWD / "solution.py").is_file() or CWD.name.startswith("day") else []
    if CWD.name == "final_project":
        required = ["PROJECT_SPEC.md", "README.md"]
    return [name for name in required if not (CWD / name).is_file()]


def check_template_untouched(path: Path, min_len: int = 40) -> bool:
    """Return True if the file still looks like an empty template."""
    if not path.is_file():
        return True
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.strip().startswith("#")]
    return len("".join(lines).strip()) < min_len


def run_pytest() -> tuple[int, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=CWD,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        return 1, "找不到 pytest，請確認虛擬環境已安裝 requirements-dev.txt。"
    except subprocess.TimeoutExpired:
        return 1, "pytest 執行超過 120 秒逾時。"
    output = result.stdout + result.stderr
    tail = "\n".join(output.splitlines()[-30:])
    return result.returncode, tail

def invoke_reviewer(day_name: str) -> None:
    prompt = (
        f"用 reviewer 子代理評分 {day_name}，直接讀取 {day_name}/ 底下的檔案與 .gate_report.md，"
        f"依 RUBRIC.md 給分，不用先問我。"
    )
    print(f"\n=== 呼叫 `claude -p` 觸發 reviewer 子代理評分 {day_name}"
          f"（--permission-mode bypassPermissions，全程無人工確認）===")
    log_path = CWD / ".gate_review.log"
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--permission-mode", "bypassPermissions"],
            cwd=CWD.parent,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        output = result.stdout + result.stderr
        log_path.write_text(output, encoding="utf-8")
        print(output)
        print(f"（reviewer 輸出已存到 {log_path.name}）")
    except FileNotFoundError:
        print(
            "找不到 claude CLI，請確認已安裝 Claude Code 且在 PATH 中；"
            f"或改成在 Claude Code 裡手動說「用 reviewer 幫我評 {day_name}」。"
        )
    except subprocess.TimeoutExpired:
        print("呼叫 reviewer 逾時（10 分鐘），請改成手動在 Claude Code 裡評分。")

def cmd_finish(force: bool = False, declare: str | None = None, review: bool = False) -> int:
    state = load_state()
    if not state.get("start_time"):
        print("尚未呼叫 start，無法 finish。")
        return 1

    minutes = state["minutes"]
    elapsed = time.time() - state["start_time"]
    forced_early = False
    if elapsed < minutes * 60:
        if not force:
            remaining = int(minutes * 60 - elapsed)
            print(f"還沒滿 {minutes} 分鐘，還差 {remaining} 秒。請先完成獨立實作階段，或加 --force 提前結束。")
            return 1
        forced_early = True
        print(f"已使用 --force 提前結束，實際只經過 {int(elapsed // 60)} 分 {int(elapsed % 60)} 秒（未滿 {minutes} 分鐘）。")

    if declare is not None:
        answer = declare
        print(f"誠實聲明（前 {minutes} 分鐘未使用 AI 寫程式碼）：{'是' if answer == 'y' else '否'}（由 --declare 提供）")
    else:
        answer = input(f"老實回答：前 {minutes} 分鐘是否完全沒有讓 AI 產生或提供程式碼？(y/n) ").strip().lower()
    declaration = answer == "y"
    state["declaration"] = declaration
    state["finish_time"] = time.time()
    save_state(state)

    missing = check_required_files()
    pytest_code, pytest_tail = run_pytest()
    notes_empty = check_template_untouched(CWD / "notes.md") if (CWD / "notes.md").is_file() else None
    ai_usage_empty = check_template_untouched(CWD / "ai_usage.md") if (CWD / "ai_usage.md").is_file() else None

    lines = [
        f"# Gate 報告：{CWD.name}",
        "",
        f"- 獨立實作計時：{minutes} 分鐘，實際經過 {int(elapsed // 60)} 分 {int(elapsed % 60)} 秒"
        + ("（使用 --force 提前結束，未滿計時）" if forced_early else ""),
        f"- 誠實聲明（前 {minutes} 分鐘未使用 AI 寫程式碼）：{'是' if declaration else '否'}",
        f"- 缺少的必要檔案：{', '.join(missing) if missing else '無'}",
        f"- pytest 結果：{'通過' if pytest_code == 0 else f'失敗 (exit code {pytest_code})'}",
        f"- notes.md 是否仍為空白模板：{'是' if notes_empty else '否' if notes_empty is not None else '檔案不存在'}",
        f"- ai_usage.md 是否仍為空白模板：{'是' if ai_usage_empty else '否' if ai_usage_empty is not None else '檔案不存在'}",
        "",
        "## pytest 輸出（節錄最後 30 行）",
        "```",
        pytest_tail,
        "```",
        "",
        "## 給評分者的說明",
        "本報告只驗證可機械檢查的項目，不包含分數。",
        "請用 Claude Code 的 reviewer 子代理（.claude/agents/reviewer.md）對照 RUBRIC.md 與實際程式碼給分；",
        "「誠實聲明」欄位無法被此程式驗證真偽，需仰賴自我要求。",
    ]
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\n報告已寫入 {REPORT_FILE.name}。")
    if review:
        invoke_reviewer(CWD.name)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="開始獨立實作計時")
    p_start.add_argument("--minutes", type=int, default=DEFAULT_MINUTES)
    p_start.add_argument("--force", action="store_true", help="重設已存在的計時")

    sub.add_parser("status", help="查詢剩餘時間")

    p_finish = sub.add_parser("finish", help="計時結束後跑測試並產生報告")
    p_finish.add_argument("--force", action="store_true", help="時間未到也強制結束（會誠實記錄在報告中）")
    p_finish.add_argument(
        "--declare",
        choices=["y", "n"],
        default=None,
        help="非互動地提供誠實聲明（前 20 分鐘是否未用 AI 寫程式），跳過互動輸入；不給則照舊互動詢問",
    )
    p_finish.add_argument(
        "--review",
        action="store_true",
        help="finish 成功後自動呼叫 claude -p 觸發 reviewer 子代理評分（會以 bypassPermissions 執行，無人工確認）",
    )

    args = parser.parse_args()
    if args.command == "start":
        return cmd_start(args.minutes, args.force)
    if args.command == "status":
        return cmd_status()
    if args.command == "finish":
        return cmd_finish(args.force, args.declare, args.review)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
