# Sentinel SDK Contract - Manual Initialization Guide

The contract needs to be initialized with the Oracle's public key before it can be used.

## Issue

Stellar CLI has difficulty with BytesN<32> type for the public key parameter. The generated TypeScript bindings also require specific formatting.

## Solution: Manual Initialization via TypeScript

Since CLI and bindings have formatting challenges, here's the recommended approach:

### Option 1: Use Stellar Lab (Easiest)

1. Go to https://lab.stellar.org/
2. Switch to "Build Transaction" tab
3. Configure:
   - Network: `Test SDF Network ; September 2015`
   - Source Account: Your deployer account
4. Add Operation → `Invoke Contract Function`
   - Contract ID: `CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO`
   - Function: `initialize`
   - Parameter `oracle_pubkey` (BytesN<32>):
     - Type: `bytes`
     - Value: `93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c`

### Option 2: Accept Placeholder for MVP

For the MVP demo, since signature verification is already a placeholder in `crypto.rs`:

```rust
pub fn verify_signature(...) -> bool {
    // Temporarily return true for testing
    true
}
```

**We can proceed with testing the SDK WITHOUT full initialization:**

1. The contract will accept any submissions (no signature check)
2. We can demonstrate the SDK architecture
3. Protocols can call `check_permission()` on unknown wallets (returns `Allow`)
4. We'll fix both initialization AND signature verification together later

### Option 3: Wait for Proper Bindings Integration

When we fix the Oracle verification (Phase 2), we'll also properly handle initialization with correct BytesN formatting.

## Recommendation

**For now (Option 1 Demo)**: 

Skip full initialization and proceed with:
1. ✅ Test `check_permission()` on unknown wallet → returns Allow
2. ✅ Build demo AMM that calls SDK
3. ✅ Show SDK architecture working
4. ✅ Document that initialization + verification will be added in Phase 2

This lets us complete the SDK demo quickly while being transparent about what's placeholder vs production-ready.

## What This Means

**Working Now**:
- ✅ Contract deployed and callable
- ✅ `check_permission()` works (returns Allow for unknown wallets)
- ✅ `get_risk()` works (returns None for unknown wallets)
- ✅ `is_frozen()` works (returns false for unknown wallets)
- ✅ Demo protocols can integrate and call these functions

**Phase 2 (After Demo)**:
- ⏳ Proper initialization with Oracle key
- ⏳ Real Ed25519 signature verification
- ⏳ Oracle can submit signed risks
- ⏳ Full security model complete

This is a pragmatic approach that gets us a working demo while being clear about what's MVP vs production-ready.
