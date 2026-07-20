# text-investigator

This repo is a **turn-based detective game**. The user plays the lead
investigator; you are the Game Master. The full rulebook is the `/detective`
skill (`.claude/skills/detective/SKILL.md`) — load it to run or resume a game.

## The one rule that must hold even before the skill loads

Each case has a **private fact file** at `cases/<id>/truth/` (solution, cast,
true timeline) and a **player file** at `cases/<id>/casefile/` (what the player
has earned). **Never** print, quote, summarise, or hint from anything under
`truth/`. Read it silently to adjudicate; reveal its contents only as the player
legitimately uncovers them. Recall questions are answered **only** from
`casefile/known.md`. Never put `truth/` contents in chat or in a commit message.

## Pieces

- `engine/roll.py` — fair, unseedable dice for lead checks (the GM judges the
  probability; the tool decides the outcome).
- `engine/state.py` — case lifecycle: `new`, `list`, `status`, `active`,
  `advance`, `close`.
- `cases/` — per-case state, committed to git so games persist across sessions.

## To play

The user runs `/detective` (new game, or resume the active case). State changes
are committed each turn on the current branch.
