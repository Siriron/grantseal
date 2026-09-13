# GrantSeal — Revision 2

## Exact runtime fix

Studio exposed the `recipient: Address` argument to the deployed contract as a Python integer. The contract then attempted to persist that integer into `Program.recipient: Address`, causing:

`AttributeError: 'int' object has no attribute 'as_bytes'`

Revision 2 changes the public `create_program` parameter to `str` and normalizes the value at the storage boundary. It accepts canonical hex addresses and also converts a 160-bit integer representation into a canonical 20-byte `Address`.

A Direct Mode regression test exercises the integer representation with `direct_vm.check_pickling = True`.

Do not deploy this revision until the Direct Mode test suite passes.
