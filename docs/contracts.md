# Smart Contract API

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

The contract source included in `contracts/grantseal.py` is the source used as the application integration reference.
