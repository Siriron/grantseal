<div align="center">
<img src="./public/favicon.svg" width="88" alt="GrantSeal logo" />

# GrantSeal
### Evidence-anchored open-source grant milestones, resolved through GenLayer consensus

![Status](https://img.shields.io/badge/status-live%20contract-22c55e?style=flat-square)
![Network](https://img.shields.io/badge/network-GenLayer%20StudioNet-6d5dfc?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20Vite%20%2B%20GenLayerJS-55e6a5?style=flat-square)

**[Live App](https://grantseal-layer.vercel.app/)** · **[Contract on StudioNet](https://explorer-studio.genlayer.com/address/0x257b34Eb0fc3C4fFBdd52775e08a95670C8382C7)** · **[Architecture](./docs/architecture.md)** · **[Deployment](./docs/deployment.md)** · **[Frontend](./docs/frontend.md)** · **[Contracts](./docs/contracts.md)**
</div>

---

## What this is

GrantSeal is a public accountability workflow for open-source grant programs. A grantor locks a repository and milestone criteria before work begins. The recipient submits an exact Git commit. A challenger may dispute the submission, the recipient may respond, and GenLayer validators independently adjudicate the locked criteria against canonical GitHub records.

**Deployed contract:** `0x257b34Eb0fc3C4fFBdd52775e08a95670C8382C7` on GenLayer StudioNet. Deployment transaction, source revision, source digest and windows are recorded in [`deployments/studionet.json`](./deployments/studionet.json); the live transactions are in [`docs/review-evidence.md`](./docs/review-evidence.md).

## Lifecycle

1. `create_program`
2. `define_milestone`
3. `lock_program`
4. `accept_program`
5. `submit_milestone`
6. `challenge_milestone`
7. `respond_to_challenge`
8. `resolve_milestone`
9. `appeal_milestone`
10. `resolve_appeal`
11. `close_program`

The four outcomes are `MET`, `PARTIALLY_MET`, `NOT_MET`, and `INCONCLUSIVE`. Each is produced by a traceable `leader_fn` branch and each has a test that reaches it (`tests/direct/test_grantseal.py::test_every_outcome_is_reachable_from_the_model_answer`). `INCONCLUSIVE` is returned when the repository or commit cannot be bound to the locked identifiers, when bounded evidence coverage is inadequate, when a fetch returns an HTTP error, or when the model's answer is unusable; it never means "the contract could not decide" by default.

**Windows are set once, at deployment.** The constructor takes `response_window_seconds` and `appeal_window_seconds` (60 seconds to 30 days each). They are stored, have no setter, and apply to every program on that deployment; `get_config()` reports them. The production defaults are 72 hours (response) and 48 hours (appeal). A review deployment may pass shorter windows so the whole lifecycle can be exercised in one sitting; `deployments/studionet.json` records exactly which values a given deployment uses.

## Evidence model

The contract does not accept evidence URLs. It derives canonical GitHub API endpoints from the locked repository identifier and exact commit SHA. Returned records are checked for repository and commit identity binding before they can influence a verdict.

## Quick start

Contract tests (they execute the real contract under the GenVM SDK in direct mode):

```bash
pip install -r requirements-dev.txt
pytest
genvm-lint check contracts/grantseal.py
```

Frontend:

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## Project structure

```text
contracts/grantseal.py       GenVM contract source
tests/direct/                Direct-mode tests that execute the real contract
deployments/                 Deployment record (address, tx, git revision, source digest, windows)
src/config/chains.js         Single source of truth for StudioNet and contract address
src/hooks/                   Wallet and contract interaction hooks
src/pages/                   Dashboard, registry, creation, detail and docs routes
src/components/              Shared UI, async and transaction components
public/                      Custom GrantSeal assets
docs/                        Architecture, deployment, frontend and contract docs
```

## Status

**Tests.** 43 direct-mode test cases run the real contract under the GenVM SDK, including the real `leader_fn`/`validator_fn` closures, with `check_pickling` enabled on the nondet paths. Only the outside world is mocked: GitHub responses and the model's answer. They therefore prove the contract's own logic: authorization, state transitions, SHA validation, deadline enforcement to the second, milestone counts, the single-appeal rule, every verdict branch, fail-closed handling of HTTP errors and unusable model output, and validator agreement or rejection when a single decision-bearing field differs. They do **not** prove how real models behave on real repositories, real network behavior, or multi-node timing; that is what the live lifecycle in `docs/review-evidence.md` is for. See [`docs/testing.md`](./docs/testing.md).

**Revision 3 corrected two contract defects and a set of test defects found by executing the suite for the first time.** See [`docs/revision-3.md`](./docs/revision-3.md). Earlier deployments are superseded.

## License

[MIT](./LICENSE)
