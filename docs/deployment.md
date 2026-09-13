# Deployment

## Intelligent Contract

- Network: GenLayer StudioNet
- Chain ID: 61999
- RPC: `https://studio.genlayer.com/api`
- Address: `0x29E654749F76722AB18F63471d11F1af1433a8ce`
- Explorer: https://explorer-studio.genlayer.com/address/0x29E654749F76722AB18F63471d11F1af1433a8ce

## Frontend

The frontend is ready for a Vercel SPA deployment. No production URL is asserted until deployment is completed.

```bash
npm install
npm run build
```

`vercel.json` rewrites all routes to `index.html` for client-side routing.

## Re-review evidence status

The production StudioNet address is fixed at `0x29E654749F76722AB18F63471d11F1af1433a8ce`. The repository intentionally does not invent a deployment transaction hash or deployed Git commit SHA when those values are not present in the supplied source. Before steward resubmission, replace the placeholders in `deployments/studionet.template.json` with the actual deployment receipt, deployment-time Git SHA, contract source digest, and passing test output from the deployment session.

The live GrantSeal lifecycle has been verified through `respond_to_challenge`. An attempted early `resolve_milestone(1)` correctly returned `AssertionError: response window still open`; the contract's response window is 72 hours.
