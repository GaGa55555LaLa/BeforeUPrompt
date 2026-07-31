"""Validate expected directory structure; this does not grade correctness."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMON = {"README.md", "solution.py", "test_solution.py", "notes.md", "ai_usage.md"}

def main() -> int:
    missing: list[str] = []
    for day in range(1, 15):
        d = ROOT / f"day{day:02d}"
        if not d.is_dir():
            missing.append(d.name)
            continue
        missing.extend(str((d / n).relative_to(ROOT)) for n in sorted(COMMON) if not (d / n).is_file())
    required = [
        "final_project/PROJECT_SPEC.md",
        "final_project/price_report/__main__.py",
        "final_project/price_report/cli.py",
        "final_project/price_report/config.py",
        "final_project/price_report/models.py",
        "final_project/price_report/parser.py",
        "final_project/price_report/scoring.py",
        "final_project/price_report/report.py",
    ]
    missing.extend(p for p in required if not (ROOT / p).is_file())
    if missing:
        print("Missing required files:")
        for p in missing: print(f"- {p}")
        return 1
    print("Directory structure is complete.")
    print("This check does not verify implementation correctness.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
