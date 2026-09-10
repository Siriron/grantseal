<div align="center">
<img src="./public/favicon.svg" width="88" alt="GrantSeal logo" />

# GrantSeal
### Evidence-anchored open-source grant milestones, resolved through GenLayer consensus

![Status](https://img.shields.io/badge/status-live%20contract-22c55e?style=flat-square)
![Network](https://img.shields.io/badge/network-GenLayer%20StudioNet-6d5dfc?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20Vite%20%2B%20GenLayerJS-55e6a5?style=flat-square)

**[Architecture](./docs/architecture.md)** · **[Deployment](./docs/deployment.md)** · **[Frontend](./docs/frontend.md)** · **[Contracts](./docs/contracts.md)**
</div>

---

## What this is

GrantSeal is a public accountability workflow for open-source grant programs. A grantor locks a repository and milestone criteria before work begins. The recipient submits an exact Git commit. A challenger may dispute the submission, the recipient may respond, and GenLayer validators independently adjudicate the locked criteria against canonical GitHub records.

**Deployed contract:** https://explorer-studio.genlayer.com/address/0x73972983906646bfc591acDCD513fA2830d52ab9

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

The four reachable outcomes are `MET`, `PARTIALLY_MET`, `NOT_MET`, and `INCONCLUSIVE`.

## Evidence model

The contract does not accept evidence URLs. It derives canonical GitHub API endpoints from the locked repository identifier and exact commit SHA. Returned records are checked for repository and commit identity binding before they can influence a verdict.

## Quick start

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
contracts/grantseal.py       Deployed GenVM contract source
src/config/chains.js         Single source of truth for StudioNet and contract address
src/hooks/                   Wallet and contract interaction hooks
src/pages/                   Dashboard, registry, creation, detail and docs routes
src/components/              Shared UI, async and transaction components
public/                      Custom GrantSeal assets
docs/                        Architecture, deployment, frontend and contract docs
```

## Status

The GenLayer StudioNet contract is deployed at `0x73972983906646bfc591acDCD513fA2830d52ab9`.

The frontend is wired to that exact address as a plain constant in `src/config/chains.js`. A production frontend URL is intentionally not claimed here until the app itself is deployed.

## License

[MIT](./LICENSE)
