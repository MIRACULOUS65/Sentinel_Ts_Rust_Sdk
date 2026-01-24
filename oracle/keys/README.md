# Oracle Keys Directory

This directory contains the Ed25519 keypair for the Oracle service.

**⚠️ IMPORTANT**: 
- `oracle_private.key` must NEVER be committed to git
- `oracle_private.key` must NEVER be shared
- `oracle_public.key` should be embedded in the Soroban contract

## Generate Keys

Run from the `oracle/` directory:

```powershell
python crypto.py --generate-keys
```

This will create:
- `oracle_private.key` - Private signing key (64 hex characters)
- `oracle_public.key` - Public verification key (64 hex characters)

## For Hackathon

Single keypair is acceptable. The public key will be hardcoded in the Soroban contract.

## For Production

Consider:
- Hardware Security Module (HSM)
- Key rotation policies
- Multi-signature schemes
- Distributed key generation
