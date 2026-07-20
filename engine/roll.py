#!/usr/bin/env python3
"""
roll.py — the fairness backbone of the detective game.

The Game Master (the AI) judges *plausibility* and assigns a *probability*.
This tool performs the actual roll, so the outcome is never authored. Rolls use
the OS entropy source (SystemRandom): they cannot be seeded, replayed, or
save-scummed. Every roll is appended to the case's turn log for a permanent,
auditable record.

Usage:
    python engine/roll.py --prob 0.35 --reason "gas-station cashier near scene"
    python engine/roll.py --prob 0.6  --reason "canvass the marina" --case harbour-light-a1b2

If --case is omitted, the currently active case (cases/ACTIVE) is used.
"""
import argparse
import datetime as _dt
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
_rng = random.SystemRandom()  # os.urandom-backed; unseedable by design


def _active_case() -> str | None:
    pointer = CASES / "ACTIVE"
    if pointer.exists():
        cid = pointer.read_text(encoding="utf-8").strip()
        return cid or None
    return None


def _log_line(case_id: str, line: str) -> None:
    log = CASES / case_id / "casefile" / "turn-log.md"
    if not log.parent.exists():
        return  # case not scaffolded; skip logging rather than crash
    with log.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Roll a lead check for the detective game.")
    ap.add_argument("--prob", type=float, required=True,
                    help="Probability of a lead, as a decimal 0.0-1.0.")
    ap.add_argument("--reason", required=True,
                    help="Short description of what is being checked.")
    ap.add_argument("--case", default=None,
                    help="Case id. Defaults to the active case.")
    ap.add_argument("--no-log", action="store_true",
                    help="Do not append the roll to the turn log.")
    args = ap.parse_args()

    if not (0.0 <= args.prob <= 1.0):
        ap.error("--prob must be a decimal between 0.0 and 1.0 "
                 "(e.g. 0.35 for a 35% chance).")

    case_id = args.case or _active_case()

    roll = _rng.random()
    hit = roll < args.prob
    result = "HIT" if hit else "MISS"
    stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Human-facing mechanical line (out-of-narrative footnote).
    print(f"🎲 lead check  p={args.prob:.2f}  \"{args.reason}\"")
    print(f"   roll {roll:.3f}  →  {result}")

    if case_id and not args.no_log:
        _log_line(case_id,
                  f"- [{stamp}] 🎲 lead check p={args.prob:.2f} "
                  f"\"{args.reason}\" → {result} (roll {roll:.3f})")
    elif not case_id:
        print("   (no active case — roll not logged)", file=sys.stderr)

    return 0 if hit else 1  # exit code mirrors result for scripting


if __name__ == "__main__":
    raise SystemExit(main())
