# Testing

```bash
pip install -r requirements-dev.txt
pytest
genvm-lint check contracts/grantseal.py
```

`genlayer-test` 0.29.2 downloads the GenVM SDK bundle on first run and needs network access. Do not run pytest with `-s`.

## What the tests execute

`tests/direct/test_grantseal.py` loads `contracts/grantseal.py` under the real GenVM SDK in direct mode and calls its public methods. `resolve_milestone` and `resolve_appeal` run the contract's real `leader_fn`, and `direct_vm.run_validator()` runs its real `validator_fn`. Only the external world is mocked: GitHub API responses and the model's answer.

| Area | Tests |
|---|---|
| Storage persistence with pickling checked | program and milestone round trip, Studio integer-address normalization, no storage object crosses into the nondet closures |
| Authorization | grantor-only, recipient-only, challenger-or-recipient-only, self-challenge blocked, wrong-state calls |
| SHA identity | short prefixes and refs rejected, exact 40-hex accepted |
| Deadlines | challenge, response, resolution and appeal boundaries, at the second, with default and short windows |
| Deploy-time windows | reported by `get_config`, bounds enforced at deployment, honoured to the second |
| Verdicts | every outcome reachable from the model's answer, case and spacing tolerance, unusable answers fail closed |
| Evidence binding | repository mismatch, HTTP 403/404/500 never treated as evidence, missing evidence |
| Appeal | independent second round that can overturn the first, single-appeal rule, resolved-count bookkeeping |
| Closure | requires every milestone terminally resolved |
| Consensus logic | validator agrees on an independent match; rejects a different outcome, a differing binding, an errored leader, junk leader output |

## What they do not prove

They do not show how real models judge real repositories, real network latency or failure, or multi-node consensus timing. The live lifecycle in `docs/review-evidence.md` covers the deployed contract; it is a separate kind of evidence.

## Harness notes (genlayer-test 0.29.2)

- `direct_vm.expect_revert` re-raises `AssertionError`, so contract `assert` guards are checked with `pytest.raises(AssertionError, match=...)`.
- `direct_vm.warp()` patches `datetime.datetime.now()` and refreshes sender/origin on `gl.message_raw`, but does not update `gl.message_raw["datetime"]`, which this contract reads. The `_warp` helper sets it on the same dict.
- Test accounts are raw `bytes`; Studio and the CLI pass `0x` hex strings, so the tests convert with `_addr()`.
