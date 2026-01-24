# Sentinel SDK Deployment Info

## Contract Deployment

**Contract ID**: `CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO`

**Network**: Stellar Testnet

**WASM Hash**: `f35b8e6697ffbe8aee91b067a1f448f36659c07278a01dae433ad4c8d0296847`

**Deployed By**: `sentinel-deployer`

**Transaction**: https://stellar.expert/explorer/testnet/tx/e99cd4e8f0d2f0f3ad20fc3ab6ea39cd1dd6730449bb785ff3d5796b8511b19f

**Contract Explorer**: https://lab.stellar.org/r/testnet/contract/CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO

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
