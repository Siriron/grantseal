# Frontend

The app uses React, Vite, React Router, lucide-react and GenLayerJS.

## Wallet safety

Browser-wallet writes use `window.ethereum`, pass the connected address directly as the account, and call an explicit StudioNet `ensureChain()` step before each write.

## Contract state

Reads decode the JSON strings returned by the three public view methods. The address exists in exactly one application location: `src/config/chains.js`.

## Transaction UX

Every write has pending UI. Resolution and appeal explain that consensus can take several minutes. A timeout after a transaction hash exists is surfaced separately from a rejected write so users are directed to the explorer rather than blindly duplicating the state-changing call.
