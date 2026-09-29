# GrantSeal steward re-review checklist

## Reproduce locally

```bash
pip install -r requirements-dev.txt
genvm-lint check contracts/grantseal.py
pytest
git rev-parse HEAD
git status --short          # must print nothing
sha256sum contracts/grantseal.py
```

## Deploy on StudioNet

Deploy `contracts/grantseal.py` with two constructor arguments, `response_window_seconds` and `appeal_window_seconds`. In Studio this is the two inputs on the deploy form. Then read `get_config()` and confirm it returns exactly what was passed. Record the deployment transaction hash and address from the explorer, not from memory.

## Lifecycle to capture

`create_program`, `define_milestone`, `lock_program`, `accept_program`, `submit_milestone` (full 40-character SHA), `challenge_milestone`, `respond_to_challenge`, an early `resolve_milestone` (must revert with `response window still open`), `resolve_milestone` after the window, `appeal_milestone`, `resolve_appeal`, `close_program`.

For each transaction: hash, consensus result, execution result, stderr, return value.
