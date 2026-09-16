# Deployment

## Intelligent Contract

- Network: GenLayer StudioNet
- Chain ID: 61999
- RPC: `https://studio.genlayer.com/api`
- Address: `0x29E654749F76722AB18F63471d11F1af1433a8ce`
- Explorer: https://explorer-studio.genlayer.com/address/0x29E654749F76722AB18F63471d11F1af1433a8ce

## Frontend

Live production URL: **https://grantseal-layer.vercel.app/**

```bash
npm install
npm run build
```

`vercel.json` rewrites all routes to `index.html` for client-side routing.

## Re-review evidence status

The production StudioNet address is fixed at `0x29E654749F76722AB18F63471d11F1af1433a8ce`. The repository intentionally does not invent a deployment transaction hash or deployed Git commit SHA when those values are not present in the supplied source. Before steward resubmission, replace the placeholders in `deployments/studionet.template.json` with the actual deployment receipt, deployment-time Git SHA, contract source digest, and passing test output from the deployment session.

The full GrantSeal lifecycle has now been verified live, end to end, on StudioNet: `create_program` → `define_milestone` → `accept_program` → `lock_program` → `submit_milestone` → `challenge_milestone` → `respond_to_challenge` → `resolve_milestone` → `appeal_milestone` → `resolve_appeal` → `close_program`. An early `resolve_milestone(1)` attempt correctly returned `AssertionError: response window still open` before the 72-hour response window elapsed — this is the precommitted deadline being enforced, not a defect. After the window elapsed, `resolve_milestone` and, later, `resolve_appeal` each independently fetched fresh evidence and re-derived the identifier-binding checks from scratch, both arriving at `INCONCLUSIVE` with `repo_bound`/`commit_bound`/`coverage` all confirmed `true`. See `docs/review-evidence.md` for the full transaction table.

Still outstanding before resubmission: the exact deploy-time Git commit SHA and the deployment transaction hash — see `docs/review-evidence.md` for the complete list. The frontend is now live at https://grantseal-layer.vercel.app/; confirm in-browser (wallet connect, program/milestone state rendering, write-transaction flow) before citing it as fully verified rather than merely reachable.
