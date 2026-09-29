# Architecture

GrantSeal has two on-chain entities:

- **Program** — grantor, recipient, repository, immutable scope state and aggregate milestone counts.
- **Milestone** — locked criteria, exact commit SHA, challenge/response context, consensus outcome and appeal state.

The frontend reads `get_counts()` and scans the currently allocated IDs through `get_program()` and `get_milestone()`. This is appropriate for the current early-stage registry and keeps the UI aligned with the public contract API.

## Evidence path

`repo_id` and `commit_sha` are locked before consensus. The contract derives GitHub endpoints, verifies returned `full_name` and `sha` identity fields, then permits those canonical records to influence adjudication.

## Consensus path

Resolution and appeal each run their own nondeterministic consensus round. The appeal re-fetches canonical records and performs a fresh judgment against the same locked criteria.

## Time

Deadlines are computed from the transaction timestamp (`gl.message_raw["datetime"]`, parsed with integer arithmetic). The response and appeal windows are constructor parameters fixed at deployment; there is no way to change them afterwards, so a deadline is always the submission or resolution time plus a value that was public before any program existed.

## Failure handling

A fetch that returns an HTTP error status is treated as absent evidence, never as a record. Any missing identity match, missing tree, or empty evidence set produces `INCONCLUSIVE` before the model is called. The model's answer is decoded from the dict the SDK returns; an unknown or malformed answer also resolves to `INCONCLUSIVE`.
