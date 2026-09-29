# Smart Contract API

## Constructor

`GrantSeal(response_window_seconds, appeal_window_seconds)`

Both are integers in seconds, between 60 and 2,592,000 (30 days); anything else reverts at deployment. They are stored once and cannot be changed. Production defaults are `259200` (72 h) and `172800` (48 h).

## Writes

- `create_program(recipient, repo_id, title, summary)`
- `define_milestone(program_id, title, criteria_json)`
- `lock_program(program_id)`
- `accept_program(program_id)`
- `submit_milestone(milestone_id, commit_sha, submission_note)`
- `challenge_milestone(milestone_id, challenge_reason)`
- `respond_to_challenge(milestone_id, response_text)`
- `resolve_milestone(milestone_id)`
- `appeal_milestone(milestone_id, appeal_reason)`
- `resolve_appeal(milestone_id)`
- `close_program(program_id)`

## Views

- `get_program(program_id)`
- `get_milestone(milestone_id)`
- `get_counts()`
- `get_config()` returns `{"response_window_seconds", "appeal_window_seconds"}`

## Rules the tests pin down

| Rule | Where enforced |
|---|---|
| Only the grantor defines milestones, locks, and closes | `define_milestone`, `lock_program`, `close_program` |
| Only the recipient accepts and submits | `accept_program`, `submit_milestone` |
| `commit_sha` must be exactly 40 hex characters | `submit_milestone` |
| The recipient cannot challenge their own submission | `challenge_milestone` |
| Challenge and response must land no later than `response_deadline` | `challenge_milestone`, `respond_to_challenge` |
| Resolution requires `now > response_deadline` (equal is still open) | `resolve_milestone` |
| Only the recipient or the challenger may appeal, once, within `appeal_deadline` | `appeal_milestone` |
| A program closes only when every milestone is terminally resolved | `close_program` |

## Outcomes

`MET`, `PARTIALLY_MET`, `NOT_MET`, `INCONCLUSIVE`. `resolve_milestone` and `resolve_appeal` both fetch the canonical GitHub records fresh, check repository and commit identity, select bounded evidence at the exact submitted SHA, and only then ask the model. If binding fails, coverage is empty, or a fetch returns an HTTP error, the result is `INCONCLUSIVE` without consulting the model. Validators re-derive the outcome and all three binding flags independently and must match exactly.

The source in `contracts/grantseal.py` is the source that is deployed; `deployments/studionet.json` records its SHA-256 and the git revision it was deployed from.
