# GrantSeal steward re-review checklist

## Before deployment

- [ ] `genvm-lint check contracts/grantseal.py`
- [ ] `pip install -r requirements-dev.txt`
- [ ] `pytest tests/direct -v`
- [ ] Review exact Git commit SHA: `git rev-parse HEAD`
- [ ] Record source digest: `sha256sum contracts/grantseal.py`

## Reproducible StudioNet deployment

```bash
genlayer network set studionet
genlayer network info
genlayer deploy --contract contracts/grantseal.py
```

Record the deployment transaction hash and contract address exactly as returned by the CLI. Finalization/acceptance alone is not proof of successful execution; inspect the deployment result before using the address.

## Source-to-revision evidence

Record all of the following in `deployments/studionet.json`:

1. `git rev-parse HEAD`
2. `git status --short` (must be clean)
3. `sha256sum contracts/grantseal.py`
4. deployment transaction hash
5. deployed contract address
6. explorer address URL
7. passing test output

## Live lifecycle evidence

Capture explorer links and resulting state for:

1. create program
2. define milestone
3. lock program
4. accept program
5. submit milestone with full 40-character SHA
6. challenge
7. respond
8. resolve after the response window
9. close program

For each transaction record:

- transaction hash/link
- submission status
- consensus/finalization status available from the network
- execution result
- resulting contract state

Do not fabricate lifecycle evidence. The final re-review package should contain only links produced by the live StudioNet execution.
