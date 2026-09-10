# Deployment

## Intelligent Contract

- Network: GenLayer StudioNet
- Chain ID: 61999
- RPC: `https://studio.genlayer.com/api`
- Address: `0x73972983906646bfc591acDCD513fA2830d52ab9`
- Explorer: https://explorer-studio.genlayer.com/address/0x73972983906646bfc591acDCD513fA2830d52ab9

## Frontend

The frontend is ready for a Vercel SPA deployment. No production URL is asserted until deployment is completed.

```bash
npm install
npm run build
```

`vercel.json` rewrites all routes to `index.html` for client-side routing.
