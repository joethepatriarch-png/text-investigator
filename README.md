# text-investigator

A turn-based detective game you play by talking to Claude Code. You are the lead
investigator for a real investigative body somewhere in the world; Claude is the
Game Master. Start `/detective`, describe what you want to investigate, and work
the case one move at a time.

It's built to run from the Claude harness in a persistent cloud environment, so
you can pick up an open case anywhere, any time — the state lives in git.

## How to play

- **Start a case:** run `/detective`. Set the region, difficulty, case type, and
  any people or angles you want in play — leave anything blank and it's rolled at
  random.
- **Take a turn:** describe one concrete action — *"Interview the harbourmaster,"*
  *"Pull the CCTV from the chandlery,"* *"Have the coroner run a tox screen."*
  Sweeping orders (*"question everyone"*) get bounced back for a first step.
- **Recall your file:** ask what you know so far — you'll get back only what
  you've actually uncovered.
- **Ask for a hint:** you'll get what a real investigator might do procedurally —
  never a nudge drawn from the solution.
- **Solve it:** when you're ready, *present your case* — culprit, motive, method.
  If you're right, the truth (and the twist the case was built around) is yours.

## What makes it tick

Three layers, kept deliberately separate:

- **Narration & judgement** — Claude generates scenes, voices witnesses, and
  rules on your actions against a private fact file written when the case begins.
- **Tooling** — a dice roller (`engine/roll.py`) decides whether an uncertain
  lead pays off, so outcomes are fair rather than authored. Claude judges *how
  likely*; the die decides *whether*.
- **State** — `engine/state.py` and the `cases/` tree track each case, the turn
  log, and the firewall between the hidden truth and the file you've earned.

## Ground rules of the world

- **Grounded and local.** Cases use the real agency with jurisdiction, real
  geography, real procedure for wherever you set them.
- **Real constraints.** Warrants need cause, forensics take time, people lawyer
  up. Mistakes cost you — but the truth stays reachable.
- **A payoff every time.** Every solve turns on something poignant, tragic, or
  darkly funny. You shouldn't crack a case without feeling it.

## Layout

```
engine/roll.py     fair lead-check dice
engine/state.py    case lifecycle (new / list / status / active / advance / close)
cases/<id>/        per-case state:
  truth/           🔒 private fact file — never revealed except as earned
  casefile/        your earned knowledge + turn log
.claude/skills/detective/SKILL.md   the Game Master's full rulebook
```
