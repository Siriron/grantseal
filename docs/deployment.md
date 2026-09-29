# Deployment

## Intelligent Contract

- Network: GenLayer StudioNet
- Chain ID: 61999
- RPC: `https://studio.genlayer.com/api`
- Address, deployment transaction, deployed git revision, source SHA-256 and windows: **`deployments/studionet.json`**

That file is written from the explorer receipt and from git after deployment. It is not shipped as a template, so there are no placeholder values in the repository to mistake for real ones.

## Constructor

`GrantSeal(response_window_seconds, appeal_window_seconds)`. Both are integers in seconds, 60 to 2,592,000. They are fixed at deployment and cannot be changed. Production defaults are `259200` (72 h) and `172800` (48 h). A review deployment may pass shorter values so the full lifecycle runs in one sitting; `get_config()` returns what a given deployment enforces, and `deployments/studionet.json` records it.

## Reproducible deployment

```bash
git status --short                 # must print nothing
git rev-parse HEAD                 # record as deployed git revision
sha256sum contracts/grantseal.py   # record as source digest
genvm-lint check contracts/grantseal.py
pytest
```

Deploy `contracts/grantseal.py` in GenLayer Studio with the two constructor arguments. Then check that the source shown for the deployed address matches `contracts/grantseal.py` at the recorded revision, and call `get_config()`.

## Frontend

Live production URL: **https://grantseal-layer.vercel.app/**

```bash
npm install
npm run build
```

`vercel.json` rewrites all routes to `index.html` for client-side routing. The contract address lives in exactly one place, `src/config/chains.js`.
