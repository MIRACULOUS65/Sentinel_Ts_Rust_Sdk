# Sentinel SDK Deployment Info

## Contract Deployment (V2 - With Signature Verification)

**Contract ID**: `CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU`

**Network**: Stellar Testnet

**WASM Hash**: `3e50ad76dc7d1a86b935378e07a0ee9582884a74a1e081309218e44d4dcfba74`

**Deployed By**: `sentinel-deployer`

**Changes from V1**:
- ✅ Implemented production Ed25519 signature verification
- ✅ Canonical JSON serialization matching Oracle
- ✅ no_std compatible cryptography

**Transaction**: https://stellar.expert/explorer/testnet/tx/f5ce69ea73faa84348051217fb47ee8e48135e6314d453f7a21dc795255e0db5

**Contract Explorer**: https://lab.stellar.org/r/testnet/contract/CD7AHSYFDSSSNN3NVWPI654KM2CR3NX5C23LSAXFDIF57HTAOW2VYBTU

## Oracle Public Key

**Hex**: `93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c`

## Status

✅ Contract deployed to testnet  
⚠️ Initialization pending (Oracle key format needs to be fixed - will use contract bindings for proper initialization)

## Next Steps

1. Generate TypeScript/Rust bindings for the contract
2. Initialize contract with Oracle public key using bindings
3. Test SDK functions (check_permission, get_risk, is_frozen)
4. Build demo protocol that integrates the SDK
