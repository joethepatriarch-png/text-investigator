#!/usr/bin/env python3
"""
state.py — case lifecycle + bookkeeping for the detective game.

Keeps the deterministic parts deterministic so the Game Master spends tokens on
narration, not on re-creating file structure every case. Pure stdlib.

Subcommands:
    new      Scaffold a new case (folders + templates), set it active.
    list     List all cases with status and turn count.
    status   Print one case's state.json (active case by default).
    active   Set the active case.
    advance  Increment the turn counter.
    close    Mark a case solved / cold / archived.

Examples:
    python engine/state.py new --title "The Harbour Light" \
        --region "Whitby, North Yorkshire, England" --difficulty hard --type homicide
    python engine/state.py status
    python engine/state.py advance
    python engine/state.py close --status solved
"""
import argparse
import datetime as _dt
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "cases"
ACTIVE = CASES / "ACTIVE"


# --------------------------------------------------------------------------- #
# Templates. The GM fills these in when generating a case. Section headers keep
# every case's private fact file consistently structured.
# --------------------------------------------------------------------------- #
TPL_PARAMETERS = """# Case parameters — {title}

- **Case id:** {case_id}
- **Region:** {region}
- **Difficulty:** {difficulty}
- **Case type:** {ctype}
- **Investigative body:** _(the real agency with jurisdiction here)_
- **Created:** {created}

## Player-supplied
_(persons of interest, area of interest, constraints the player named)_

## Rolled at random
_(anything the player left to chance)_
"""

TPL_SOLUTION = """# SOLUTION — {title}
> 🔒 FIREWALL — never shown, quoted, or summarised to the player.
> Read silently to adjudicate. The player learns this only by earning it.

## The truth, in one line

## What actually happened

## Who did it, and why

## The dramatic core
_(the poignant / tragic / darkly funny thing that makes the solve land —
this is the player's real reward. Decide it now, not later.)_

## The evidence trail
_(the chain by which a competent investigator could uncover the truth)_

## Red herrings
_(what misleads, and exactly how — scaled to difficulty)_

## Fail conditions
_(what would let the case go cold or an arrest fall apart — recoverable)_
"""

TPL_CAST = """# CAST & LOCATIONS — {title}
> 🔒 FIREWALL — private. `revealed:` flags track what the player has earned.

## People
<!-- For each: name, role, what they KNOW, what they'll SAY vs HIDE,
     whether they lie, and revealed: no/partial/yes -->

## Locations
<!-- For each: what's here, what evidence it holds, and revealed status -->
"""

TPL_TIMELINE = """# TIMELINE (true) — {title}
> 🔒 FIREWALL — the real sequence of events. Private.

<!-- Chronological ground truth. Include the offence, and the ordinary
     movements of everyone involved, so alibis and contradictions are consistent. -->
"""

TPL_KNOWN = """# CASE FILE — {title}
> The player's earned knowledge. Recall questions are answered ONLY from here.
> Everything below was legitimately uncovered through investigation.

## The opening
_(what the investigator knows at the very start)_

## Established facts

## Open threads
"""

TPL_TURNLOG = """# TURN LOG — {title}
> Chronological record of actions, outcomes, and dice rolls.

"""


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "case"


def _read_state(case_id: str) -> dict:
    p = CASES / case_id / "state.json"
    if not p.exists():
        sys.exit(f"error: no such case '{case_id}'")
    return json.loads(p.read_text(encoding="utf-8"))


def _write_state(case_id: str, data: dict) -> None:
    p = CASES / case_id / "state.json"
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _active() -> str | None:
    if ACTIVE.exists():
        return ACTIVE.read_text(encoding="utf-8").strip() or None
    return None


def _resolve(case_arg: str | None) -> str:
    cid = case_arg or _active()
    if not cid:
        sys.exit("error: no case specified and no active case set")
    return cid


def cmd_new(args) -> None:
    created = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    case_id = f"{_slug(args.title)}-{secrets.token_hex(2)}"
    base = CASES / case_id
    if base.exists():
        sys.exit(f"error: case '{case_id}' already exists")

    (base / "truth").mkdir(parents=True)
    (base / "casefile").mkdir(parents=True)

    fields = dict(title=args.title, case_id=case_id, region=args.region,
                  difficulty=args.difficulty, ctype=args.type, created=created)
    (base / "parameters.md").write_text(TPL_PARAMETERS.format(**fields), encoding="utf-8")
    (base / "truth" / "solution.md").write_text(TPL_SOLUTION.format(**fields), encoding="utf-8")
    (base / "truth" / "cast.md").write_text(TPL_CAST.format(**fields), encoding="utf-8")
    (base / "truth" / "timeline.md").write_text(TPL_TIMELINE.format(**fields), encoding="utf-8")
    (base / "casefile" / "known.md").write_text(TPL_KNOWN.format(**fields), encoding="utf-8")
    (base / "casefile" / "turn-log.md").write_text(TPL_TURNLOG.format(**fields), encoding="utf-8")

    _write_state(case_id, {
        "case_id": case_id,
        "title": args.title,
        "status": "active",
        "turn": 0,
        "region": args.region,
        "difficulty": args.difficulty,
        "type": args.type,
        "created": created,
    })
    ACTIVE.write_text(case_id + "\n", encoding="utf-8")

    print(f"created case: {case_id}")
    print(f"  path:   cases/{case_id}/")
    print(f"  active: yes")
    print("Now fill in truth/solution.md, truth/cast.md, truth/timeline.md, "
          "then seed casefile/known.md with the opening.")


def cmd_list(_args) -> None:
    if not CASES.exists():
        print("(no cases yet)")
        return
    active = _active()
    rows = []
    for d in sorted(CASES.iterdir()):
        sj = d / "state.json"
        if sj.is_file():
            s = json.loads(sj.read_text(encoding="utf-8"))
            mark = "*" if s["case_id"] == active else " "
            rows.append((mark, s["case_id"], s.get("status", "?"),
                         s.get("turn", 0), s.get("title", "")))
    if not rows:
        print("(no cases yet)")
        return
    print(f"{'':1} {'CASE ID':28} {'STATUS':9} {'TURN':>4}  TITLE")
    for mark, cid, status, turn, title in rows:
        print(f"{mark:1} {cid:28} {status:9} {turn:>4}  {title}")
    print("\n* = active case")


def cmd_status(args) -> None:
    s = _read_state(_resolve(args.case))
    print(json.dumps(s, indent=2))


def cmd_active(args) -> None:
    cid = args.case
    _read_state(cid)  # validates existence
    ACTIVE.write_text(cid + "\n", encoding="utf-8")
    print(f"active case: {cid}")


def cmd_advance(args) -> None:
    cid = _resolve(args.case)
    s = _read_state(cid)
    s["turn"] = int(s.get("turn", 0)) + 1
    _write_state(cid, s)
    print(f"{cid} → turn {s['turn']}")


def cmd_close(args) -> None:
    cid = _resolve(args.case)
    s = _read_state(cid)
    s["status"] = args.status
    _write_state(cid, s)
    print(f"{cid} → status {args.status}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Case lifecycle for the detective game.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="scaffold a new case and set it active")
    p.add_argument("--title", required=True)
    p.add_argument("--region", default="(unspecified)")
    p.add_argument("--difficulty", default="medium")
    p.add_argument("--type", default="(unspecified)")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("list", help="list all cases")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("status", help="print a case's state")
    p.add_argument("--case", default=None)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("active", help="set the active case")
    p.add_argument("case")
    p.set_defaults(func=cmd_active)

    p = sub.add_parser("advance", help="increment the turn counter")
    p.add_argument("--case", default=None)
    p.set_defaults(func=cmd_advance)

    p = sub.add_parser("close", help="set case status")
    p.add_argument("--status", required=True,
                   choices=["active", "solved", "cold", "archived"])
    p.add_argument("--case", default=None)
    p.set_defaults(func=cmd_close)

    args = ap.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
