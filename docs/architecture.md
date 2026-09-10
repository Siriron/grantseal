# Architecture

GrantSeal has two on-chain entities:

- **Program** — grantor, recipient, repository, immutable scope state and aggregate milestone counts.
- **Milestone** — locked criteria, exact commit SHA, challenge/response context, consensus outcome and appeal state.

The frontend reads `get_counts()` and scans the currently allocated IDs through `get_program()` and `get_milestone()`. This is appropriate for the current early-stage registry and keeps the UI aligned with the public contract API.

## Evidence path

`repo_id` and `commit_sha` are locked before consensus. The contract derives GitHub endpoints, verifies returned `full_name` and `sha` identity fields, then permits those canonical records to influence adjudication.

## Consensus path

Resolution and appeal each run their own nondeterministic consensus round. The appeal re-fetches canonical records and performs a fresh judgment against the same locked criteria.
