# GrantSeal, Revision 3

Revision 3 is the first revision whose tests were actually executed against the contract. Executing them exposed defects that earlier live runs could not show.

## Contract defects fixed

1. **Every verdict collapsed to `INCONCLUSIVE`.** `gl.nondet.exec_prompt(..., response_format="json")` returns a `dict`. `_parse_outcome` passed it to `json.loads`, which raised `TypeError`, and a blanket `except` turned that into `INCONCLUSIVE`. Given the SDK's documented return type and the direct-mode reproduction, `MET`, `PARTIALLY_MET` and `NOT_MET` were unreachable whatever the model answered. The earlier live rounds that ended `INCONCLUSIVE` with all binding checks true are consistent with this defect, and the previous evidence document presented them as a substantive judgment, which it had no basis to do. Whether a live model now returns the other outcomes is confirmed by the live lifecycle in `docs/review-evidence.md`, not by these tests. `_parse_outcome` now decodes the dict directly, still accepts a string, normalizes case and spacing, and fails closed on anything else.
2. **HTTP errors were not detected.** `_fetch_json` read `response.status_code`, which the SDK response does not have (it has `status`), so the `>= 400` check never ran. It now reads `status`.
3. **Windows were hardcoded.** The 72 h and 48 h windows are now constructor parameters, bounded to 60 s to 30 days, stored once and immutable, and reported by `get_config()`. This lets a review deployment exercise the full lifecycle in one sitting while the production defaults stay 72 h and 48 h.
4. A bare `Exception` in `define_milestone` became `gl.vm.UserError`, which clears the linter warning.

## Test defects fixed

The suite had never run. It passed `str(bytes)` as an address, used mock URL patterns with an escaped backslash that never matched, relied on `warp()` reaching a clock the harness does not update, and used `expect_revert` for `AssertionError` guards, which it does not catch. It also never exercised any verdict other than the one it mocked, which is how defect 1 survived. All fixed, and 29 tests added.

## How the suite was checked

Each of these was reintroduced separately into a scratch copy and the suite was required to fail: the `status_code` read (4 tests fail), the `json.loads(dict)` parse (9 fail), a validator that ignores the outcome (1 fails), removal of the response-deadline check (2 fail), and windows that ignore the constructor (3 fail). With the fixes in place all 43 pass.

## Superseded deployments

Contracts deployed from earlier revisions are superseded and should not be cited as evidence of this contract's behavior.
