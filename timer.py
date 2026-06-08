"""
Focus Timer — Pomodoro-style terminal timer with ASCII clock and session log.

Usage:
  python timer.py            # 25-min focus + 5-min break (default)
  python timer.py 45 10      # custom focus/break in minutes
"""

import sys
import time
import os
import datetime
import threading
import msvcrt  # Windows keyboard input

# ── ASCII digit segments (7-segment style, 5 rows tall) ──────────────────────
DIGITS = {
    "0": ["┌─┐", "│ │", "│ │", "│ │", "└─┘"],
    "1": ["  │", "  │", "  │", "  │", "  │"],
    "2": ["┌─┐", "  │", "┌─┘", "│  ", "└─┘"],
    "3": ["┌─┐", "  │", " ─┤", "  │", "└─┘"],
    "4": ["│ │", "│ │", "└─┤", "  │", "  │"],
    "5": ["┌─┐", "│  ", "└─┐", "  │", "└─┘"],
    "6": ["┌─┐", "│  ", "├─┐", "│ │", "└─┘"],
    "7": ["┌─┐", "  │", "  │", "  │", "  │"],
    "8": ["┌─┐", "│ │", "├─┤", "│ │", "└─┘"],
    "9": ["┌─┐", "│ │", "└─┤", "  │", "└─┘"],
    ":": ["   ", " ● ", "   ", " ● ", "   "],
}


def render_time(seconds: int) -> str:
    mm = f"{seconds // 60:02d}"
    ss = f"{seconds % 60:02d}"
    chars = list(mm[0]) + list(mm[1]) + [":"] + list(ss[0]) + list(ss[1])
    rows = []
    for row in range(5):
        rows.append("  ".join(DIGITS[c][row] for c in chars))
    return "\n".join(rows)


def beep(n=3):
    for _ in range(n):
        print("\a", end="", flush=True)
        time.sleep(0.3)


def log_session(label: str, duration_min: int, log_path: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{ts}  {label:<10}  {duration_min} min\n")


def progress_bar(elapsed: int, total: int, width: int = 40) -> str:
    filled = int(width * elapsed / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * elapsed / total)
    return f"[{bar}] {pct:3d}%"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def run_phase(label: str, total_seconds: int, color_code: str, log_path: str):
    start = time.time()
    interrupted = False

    print(f"\n  {color_code}▶  {label}\033[0m  (press Q to skip)\n")
    time.sleep(1)

    while True:
        elapsed = int(time.time() - start)
        remaining = total_seconds - elapsed
        if remaining <= 0:
            break

        # Non-blocking key check on Windows
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
            if key == "q":
                interrupted = True
                break

        clear()
        print(f"\n  {color_code}▶  {label}\033[0m  (press Q to skip)\n")
        print(render_time(remaining))
        print()
        print("  " + progress_bar(elapsed, total_seconds))
        print()
        time.sleep(1)

    if not interrupted:
        beep(3)
        log_session(label, total_seconds // 60, log_path)
        clear()
        print(f"\n  {color_code}✔  {label} complete!\033[0m\n")
        time.sleep(2)
    else:
        print(f"\n  Skipped {label}.\n")
        time.sleep(1)


def show_log(log_path: str):
    if not os.path.exists(log_path):
        print("  No sessions logged yet.")
        return
    print("\n  \033[1mSession Log\033[0m")
    print("  " + "─" * 38)
    with open(log_path, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[-15:]:  # show last 15
        print("  " + line.rstrip())
    print()


def main():
    focus_min = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    break_min = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    log_path = os.path.join(os.path.dirname(__file__), "sessions.log")

    clear()
    print("""
  ╔══════════════════════════════════╗
  ║       🍅  FOCUS  TIMER           ║
  ╚══════════════════════════════════╝
""")
    print(f"  Focus: \033[32m{focus_min} min\033[0m   Break: \033[34m{break_min} min\033[0m")
    print(f"  Log  : {log_path}")
    print()
    print("  Commands during timer:  Q = skip phase")
    print()

    while True:
        print("  ┌─────────────────────┐")
        print("  │  S = start session  │")
        print("  │  L = view log       │")
        print("  │  Q = quit           │")
        print("  └─────────────────────┘")
        print()
        key = msvcrt.getch().decode("utf-8", errors="ignore").lower()

        if key == "s":
            run_phase("FOCUS", focus_min * 60, "\033[32m", log_path)
            run_phase("BREAK", break_min * 60, "\033[34m", log_path)
            clear()
            print("""
  ╔══════════════════════════════════╗
  ║       🍅  FOCUS  TIMER           ║
  ╚══════════════════════════════════╝
""")
            print(f"  Focus: \033[32m{focus_min} min\033[0m   Break: \033[34m{break_min} min\033[0m\n")
        elif key == "l":
            clear()
            show_log(log_path)
        elif key == "q":
            print("\n  Goodbye! Stay focused. 👋\n")
            break


if __name__ == "__main__":
    main()
