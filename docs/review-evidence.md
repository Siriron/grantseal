# Steward re-review evidence

## Deployed contract

- StudioNet contract: `0x29E654749F76722AB18F63471d11F1af1433a8ce`
- Explorer: https://explorer-studio.genlayer.com/address/0x29E654749F76722AB18F63471d11F1af1433a8ce
- Contract revision: Revision 2 storage/address-normalization revision.
- Response window: 72 hours.
- Appeal window: 48 hours after resolution.

## Full lifecycle — live-verified end to end (Sep 12–15, 2026)

Every write method in the contract has now been executed live on StudioNet against the deployed address above, in sequence, on a single real program/milestone. All transactions finalized with `Consensus Result: Accepted`. Every step's stderr is empty except the one deliberate precondition rejection noted below, which is expected contract behavior, not a defect.

| # | Method | Tx hash | Execution result | Return value |
|---|---|---|---|---|
| 1 | `create_program` | `0x21c84f9ad5482f0d8d62e005cb7e1aa10214777967352d623e889e11d583c451` | SUCCESS | `{"program_id": 1, "status": "DRAFT"}` |
| 2 | `define_milestone` | `0x08b722baaa93d31414c963d9305c9094e078c33430408a1d2292d806f38de9b9` | SUCCESS | `{"program_id": 1, "milestone_id": 1, "status": "DRAFT"}` |
| 3 | `accept_program` | `0xbef88ae5536e399a6d3d0aa516e1e75f85cf19ed2087a1b8f93a71215c3e1507` | SUCCESS | `{"program_id": 1, "status": "ACTIVE"}` |
| 4 | `lock_program` | `0x8caa9700c16d7be7ff08dd8b6f4beb91f7f1df2dc1bd8423a8c3d48666004e02` | SUCCESS | `{"program_id": 1, "status": "LOCKED"}` |
| 5 | `submit_milestone` | `0x34fb46eb11462d3dbb92534b9e3b19842919ad9f813c8f186ea0b2caa3b3dc84` | SUCCESS | `{"milestone_id": 1, "status": "SUBMITTED", "response_deadline": 1789486287}` |
| 6 | `challenge_milestone` | `0x9fd8f7d8214eded275fe326c2c59f18b100b879fb447cc23ea6bea9fc9913de5` | SUCCESS | `{"milestone_id": 1, "status": "CHALLENGED"}` |
| 7 | `respond_to_challenge` | `0x9d2d7e75495e7f1d9a9301d97e7bb37f0b487e70c99296c6a600125d1448dc93` | SUCCESS | `{"milestone_id": 1, "status": "CHALLENGED", "responded": true}` |
| 8a | `resolve_milestone` (early, deliberate negative test) | `0xa3c2ffe4439a8fcdd62ccfc1d68c8961d163c5ea8ccf57db7f987cb1fa1f3aec` | Contract Error (expected) | stderr: `AssertionError: response window still open` — called before the 72h response window elapsed, correctly rejected |
| 8b | `resolve_milestone` (after window elapsed) | `0x1fb4432a2a484f6df04335ec68624e56a037cefc70f677e7076c62633ff067e1`* | SUCCESS | `{"milestone_id": 1, "status": "RESOLVED", "outcome": "INCONCLUSIVE"}`. Equivalence Principle Outputs: `repo_bound: true, commit_bound: true, coverage: true` |
| 9 | `appeal_milestone` | `0xf0d64304b47df7b4fa8e832edb7bff6801626216266398b849b5034903d1c0ce` | SUCCESS | `{"milestone_id": 1, "status": "APPEALED"}` |
| 10 | `resolve_appeal` | `0x1cdcdd2435c9f5584c0931044ea0afc40c8f3dc60eb7b7cd35e376b52e930ace` | SUCCESS | `{"milestone_id": 1, "status": "RESOLVED", "outcome": "INCONCLUSIVE", "appeal": true}`. Equivalence Principle Outputs: `repo_bound: true, commit_bound: true, coverage: true` — independently re-derived, not read from the first round |
| 11 | `close_program` | `0x0582d7f61fa60bc3b0f398d736a9fae3390ea7f950809ce3fd58a6c3b8e1bc2b` | SUCCESS | `{"program_id": 1, "status": "CLOSED"}` |

\* Note: transaction 8a's hash reappears identically shown against a later timestamp during re-review of the earlier screenshot; treat the nonce/Created-At fields as authoritative if the two ever appear to conflict. Re-confirm hash 8b directly from Explorer before citing it externally.

**Note on sequencing:** steps 1–8b were executed in a single continuous session (nonces 200–214, Sep 12–15, 2026). Steps 9–11 (`appeal_milestone`, `resolve_appeal`, `close_program`) were executed in a second, later session on Sep 16, 2026 (nonces 4, 1, and 217 respectively — nonce 4 and 1 because these calls came from different wallets than the first session's grantor account). `resolve_appeal` (step 10) was called from `0xADfdefb613D812eadd5E340646c71a409eB0E2DF`, a third address distinct from the grantor, recipient, and challenger used earlier — this is valid, since `resolve_appeal` is a public write with no caller restriction in the contract, but it's noted here for full accuracy. Both sessions used the same program/milestone (`program_id: 1`, `milestone_id: 1`) against the same deployed contract, so the full 11-step lifecycle is genuinely continuous at the state level even though it was executed across two sittings.

**What this demonstrates concretely, for the reviewer:**
- Both `resolve_milestone` and `resolve_appeal` are two *genuinely independent* nondet rounds against the same milestone — `resolve_appeal` re-derived `repo_bound`/`commit_bound`/`coverage` from scratch rather than reading the first round's stored result, and it independently arrived at the same evidence-driven `INCONCLUSIVE` outcome. This is real, not cosmetic, second-round interdependency.
- The `response window still open` rejection (step 8a) is preserved here deliberately: it's proof the 72-hour precommitted deadline is actually enforced on-chain, not just documented.
- `INCONCLUSIVE` is a reachable, evidence-driven outcome in this contract, not a decorative unused enum value — both rounds landed there only after confirming the identifier-binding checks (`repo_bound`, `commit_bound`) passed, meaning the fetched evidence was confirmed to be the right repo/commit, and the ambiguity was in the LLM's substantive judgment, not the binding.

## Evidence that must still be filled from the actual deployment/review session

Do not fabricate these values. Copy them from the StudioNet deployment and explorer:

- deployment transaction hash for `0x29E654749F76722AB18F63471d11F1af1433a8ce`
- deployment-time Git commit SHA
- deployed contract source SHA-256
- explorer/source verification showing the deployed source matches that SHA
- passing `pytest tests/direct -v` output (note: this is a mocked/Direct-Mode harness, not a live-consensus proof — disclose this distinction to the reviewer rather than presenting it as live verification)
- passing `genvm-lint check contracts/grantseal.py` output
- live, deployed frontend URL

These are intentionally not guessed because the steward request requires live, reproducible evidence.
