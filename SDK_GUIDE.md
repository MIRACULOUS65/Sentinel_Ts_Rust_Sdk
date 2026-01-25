# Sentinel SDK - End-to-End Build Guide

This guide explains how we built the Sentinel SDK and how you can compile and deploy it yourself.

## 🏗️ What We Built

The Sentinel SDK is a **Soroban Smart Contract** written in Rust. It serves as the on-chain "enforcement layer" for our AI risk engine.

### Core Components (`blockchain/contracts/sentinel-sdk/src/`)

1.  **`lib.rs`**: The main contract logic.
    *   **`initialize`**: Sets the reliable Oracle public key.
    *   **`submit_risk`**: Allows *only* the Oracle to update risk scores (verified by signature).
    *   **`check_permission`**: The function protocols call. It returns `Allow`, `Limit`, or `Freeze`.

2.  **`types.rs`**: Defines the data allowed on-chain.
    *   `RiskState`: The struct stored for each wallet (score, timestamp, decision).

3.  **`crypto.rs`**: Security logic.
    *   Verifies **Ed25519 signatures** to ensure risk scores actually came from our AI Oracle and weren't faked.

## 🚀 How to Build & Deploy

### Prerequisites
- [Rust](https://rustup.rs/) (with `wasm32-unknown-unknown` target)
- [Stellar CLI](https://developers.stellar.org/docs/build/smart-contracts/getting-started/setup)

### Step 1: Compile the Contract
Navigate to the contract directory:
```bash
cd blockchain/contracts/sentinel-sdk
```

Build the optimized WASM file:
```bash
stellar contract build
```
*Output: `target/wasm32-unknown-unknown/release/sentinel_sdk.wasm`*

### Step 2: Deploy to Testnet
1.  **Generate an Identity**:
    ```bash
    stellar keys generate --global deployer --network testnet
    stellar keys fund deployer --network testnet
    ```

2.  **Deploy**:
    ```bash
    stellar contract deploy \
      --wasm target/wasm32-unknown-unknown/release/sentinel_sdk.wasm \
      --source deployer \
      --network testnet
    ```
    *Copy the **Contract ID** returned (e.g., `CD...`)*.

### Step 3: Initialize
You must tell the SDK who the trusted Oracle is. Use the Oracle's Public Key (from the Oracle Service).

```bash
stellar contract invoke \
  --id <YOUR_CONTRACT_ID> \
  --source deployer \
  --network testnet \
  -- initialize \
  --oracle_pubkey <ORACLE_PUBLIC_KEY>
```

## 🔌 How Protocols Use It

Any other contract can now import your SDK and call:

```rust
let sentinel = SentinelClient::new(&env, &sentinel_contract_id);
let decision = sentinel.check_permission(&user_wallet);

match decision {
    RiskDecision::Allow => { /* Proceed */ },
    RiskDecision::Freeze => { panic!("Wallet is risky!") }
}
```

This completes the loop: **AI Analysis (Service 2) -> Oracle Sign -> SDK Verify -> Protocol Enforce**.
