# Steward re-review evidence

All values below were read from the StudioNet explorer page for the deployed contract, not typed from memory.

## Superseded deployments

`0x29E654749F76722AB18F63471d11F1af1433a8ce`, its transactions, and the earlier 11-step table are withdrawn. That contract could only return `INCONCLUSIVE` (`docs/revision-3.md`, defect 1), so it does not demonstrate this contract's behavior. An intermediate deployment attempt made with both windows set to `0` was rejected by the constructor (`response window out of range`) and never initialized; it is not used.

## Current deployment

- Contract: `0x257b34Eb0fc3C4fFBdd52775e08a95670C8382C7`
- Explorer: https://explorer-studio.genlayer.com/address/0x257b34Eb0fc3C4fFBdd52775e08a95670C8382C7
- Deployment tx: `0x010b7878376efea6c7d72313d3e1d801d01fa935a2f81b2e35711d08f1dc6faf`, constructor SUCCESS, Accepted, Finalized
- Deployer and grantor: `0x27b79B11aeC2ffC17C3115EEb472EC4fd015F635`. Recipient: `0x40edE296E01e1D57b25697b07D0f1c69077843D0`
- Windows in force, read from the contract with `get_config()` in Studio Run and Debug: `{"response_window_seconds": 600, "appeal_window_seconds": 900}`. Consistent with `submit_milestone` returning `response_deadline` 1790649668, which is 02:41:08 UTC for a submission at 02:31:08 UTC.

Git revision and source digest are in `deployments/studionet.json` when recorded from the deployed commit.

## Live lifecycle, program 1, milestone 1

The graded submission is commit `117a9ad4a6f0d08eb0cdb88c27b894ede593a858`, the commit the contract judged. It is not the deployed source revision.

| Step | Method | Sender | Result | Tx |
|---|---|---|---|---|
| 1 | `create_program` | grantor | SUCCESS | `0x9320e5a807d3a2a2ecd77a67283052f91320bf3b4dceced9994236588f00ceec` |
| 2 | `define_milestone` | grantor | SUCCESS | `0x4e3c81541896f112b96b874bd012107cf57c5e9c1ce0ce04d6ba65e563141978` |
| 3 | `lock_program` | grantor | SUCCESS | `0x2627e959fb6fb6e1366d160cf6c7a515fa1ac0b104c54d4de5fea4991890a6ca` |
| 4 | `accept_program` | recipient | SUCCESS | `0x65c5c3cdddacc749c148db666ee7a6ac31d8d583a5825f5430a8cc711aa06f56` |
| 5 | `submit_milestone` | recipient | SUCCESS, `response_deadline` 1790649668 | `0xcc79e263f2cac2449715ae73d96418465fff9ff104491276926b63e2e29071d3` |
| 6 | `challenge_milestone` | grantor | SUCCESS, `CHALLENGED` | `0xd3d506bbd503da2dd1c8cb0e284cc54f0d9eb1d33b66e617b0cb15f069f63d3e` |
| 7 | `respond_to_challenge` | recipient | SUCCESS, `responded: true` | `0x561590fef5d25a63a54c4c9fc9248cb631c6156e0f869a6e07c6877750cb3d86` |
| 8a | `resolve_milestone` (early) | recipient | reverted: `response window still open` | `0xe414cdc1356d17736f4bcd65560dd11e897c326b8e88bbe377a6277b4719f279` |
| 8b | `resolve_milestone` | recipient | SUCCESS, `outcome: MET` | `0xd12d3d91fae8caf85ef65d4b73372f489ccb2e15f396ba472d9fe45c0e27dfac` |
| 9 | `appeal_milestone` | grantor (challenger) | SUCCESS | `0xb27787dc74bc2f8fbd11396f6a81aea9977cb53d98a74a82085134f26bae6cf3` |
| 10 | `resolve_appeal` | grantor | SUCCESS, `outcome: MET`, `appeal: true` | `0x0a642f9b1e8e4a846db10776313339a6fce96c760cba8ad6ca9bb1b2fce9da5d` |
| 11 | `close_program` | grantor | SUCCESS, `CLOSED` | `0xf885d8527bf3e67082aa32ed0278f041f67e45a58c833775f571987d2156b626` |

Every non-reverted call: execution SUCCESS, consensus Accepted, stderr empty, five validators, zero rotations. Step 8b and step 10 each show `repo_bound`, `commit_bound` and `coverage` all `true` in the consensus output.

The explorer also lists one reverted `respond_to_challenge`, `0x6c38c568ce112e953cbef40f60c2816d18d4d91d744d2232966c2270c5e51321`, sent by mistake from the grantor wallet before the recipient's successful call. It reverted with `AssertionError: only recipient` (contract line 582), which is a live check that only the locked recipient can respond.

## What this shows and does not show

- The deadline is enforced on chain: the early resolve reverted, the later one succeeded.
- Both resolution rounds fetched GitHub fresh, bound the repository and commit, and reached `MET` by consensus.
- The appeal reached the same outcome as the first round. That the appeal can overturn the first outcome is shown by the direct-mode test `test_appeal_is_an_independent_round_that_can_overturn_the_first_outcome`, not by this live run.
- The fail-closed path for a nonexistent commit and for HTTP errors was not run live. It is covered by direct-mode tests (`test_http_error_never_becomes_evidence`, `test_repository_identity_mismatch_is_inconclusive_even_if_model_says_met`).
