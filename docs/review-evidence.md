# Steward re-review evidence

## Deployed contract

- StudioNet contract: `0x29E654749F76722AB18F63471d11F1af1433a8ce`
- Explorer: https://explorer-studio.genlayer.com/address/0x29E654749F76722AB18F63471d11F1af1433a8ce
- Contract revision: Revision 2 storage/address-normalization revision.
- Response window: 72 hours.
- Appeal window: 48 hours after resolution.

## Live evidence currently confirmed

The live deployment has successfully executed:

1. `create_program`
2. `define_milestone`
3. `lock_program`
4. `accept_program`
5. `submit_milestone`
6. `challenge_milestone`
7. `respond_to_challenge`

A subsequent early `resolve_milestone(1)` was finalized with consensus `Accepted` but execution `Contract Error` and stderr:

`AssertionError: response window still open`

This is expected contract behavior because the 72-hour response window had not elapsed.

## Evidence that must be filled from the actual deployment/review session

Do not fabricate these values. Copy them from the StudioNet deployment and explorer:

- deployment transaction hash
- deployment-time Git commit SHA
- deployed contract source SHA-256
- explorer/source verification showing the deployed source matches that SHA
- passing `pytest tests/direct -v` output
- passing `genvm-lint check contracts/grantseal.py` output
- final successful `resolve_milestone(1)` transaction
- appeal transaction and `resolve_appeal(1)` transaction, if the appeal branch is exercised
- final `close_program(1)` transaction and resulting state

These are intentionally not guessed because the steward request requires live, reproducible evidence.
