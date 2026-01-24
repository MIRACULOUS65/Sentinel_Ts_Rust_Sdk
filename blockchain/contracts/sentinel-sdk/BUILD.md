# Sentinel SDK - Build & Test Guide

Quick reference for building and testing the Sentinel SDK contract.

## 🛠️ Prerequisites

1. **Install Rust**:
   ```powershell
   # Install rustup from https://rustup.rs/
   rustup default stable
   rustup target add wasm32-unknown-unknown
   ```

2. **Install Stellar CLI**:
   ```powershell
   cargo install --locked stellar-cli --features opt
   ```

3. **Configure Testnet**:
   ```powershell
   stellar network add --global testnet `
     --rpc-url https://soroban-testnet.stellar.org:443 `
     --network-passphrase "Test SDF Network ; September 2015"
   ```

## 🔨 Building

```powershell
# Navigate to contract directory
cd d:\sentinel_local\Sentinel\blockchain\contracts\sentinel-sdk

# Build with Cargo
cargo build --target wasm32-unknown-unknown --release

# Or use Stellar CLI (recommended)
stellar contract build
```

Output: `target/wasm32-unknown-unknown/release/sentinel_sdk.wasm`

## 🧪 Testing

```powershell
# Run all tests
cargo test

# Run specific test
cargo test test_initialize

# Run tests with output
cargo test -- --nocapture
```

## 🚀 Deployment

### 1. Create Deployer Identity

```powershell
stellar keys generate --global sentinel-deployer --network testnet
```

### 2. Fund Account

```powershell
stellar keys fund sentinel-deployer --network testnet
```

### 3. Deploy Contract

```powershell
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/sentinel_sdk.wasm \
  --source sentinel-deployer \
  --network testnet
```

**Save the Contract ID!** (e.g., `CAAAAAAAAAAAAAAAAAAA...`)

### 4. Initialize with Oracle Public Key

```powershell
# Use Oracle public key: 93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c

stellar contract invoke \
  --id <CONTRACT_ID> \
  --source sentinel-deployer \
  --network testnet \
  -- initialize \
  --oracle_pubkey 93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c
```

## ✅ Verify Deployment

### Check Oracle Public Key

```powershell
stellar contract invoke \
  --id <CONTRACT_ID> \
  --source sentinel-deployer \
  --network testnet \
  -- get_oracle_pubkey
```

Should return: `93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c`

### Query Unknown Wallet (should allow)

```powershell
stellar contract invoke \
  --id <CONTRACT_ID> \
  --source sentinel-deployer \
  --network testnet \
  -- check_permission \
  --wallet <SOME_WALLET_ADDRESS>
```

Should return: `Allow`

## 📊 Common Commands

### Check if Wallet is Frozen

```powershell
stellar contract invoke \
  --id <CONTRACT_ID> \
  --network testnet \
  -- is_frozen \
  --wallet <WALLET_ADDRESS>
```

### Get Risk State

```powershell
stellar contract invoke \
  --id <CONTRACT_ID> \
  --network testnet \
  -- get_risk \
  --wallet <WALLET_ADDRESS>
```

## 🔗 Integration with Oracle

Once deployed, the Oracle service can submit risks:

```python
# In Oracle service or separate script
import requests
from stellar_sdk import SorobanServer, Keypair, TransactionBuilder

# 1. Get signed risk from Oracle
oracle_response = requests.post(
    "http://localhost:8001/sign-risk",
    json={
        "wallet": "GABCD...",
        "risk_score": 87,
        "reason": "abnormal transfers"
    }
).json()

# 2. Submit to Sentinel SDK contract
# (Use Stellar SDK to call submit_risk)
```

## 🐛 Troubleshooting

### Build fails
```powershell
# Clean and rebuild
cargo clean
cargo build --target wasm32-unknown-unknown --release
```

### Tests fail
```powershell
# Update dependencies
cargo update
cargo test
```

### Deployment fails
```powershell
# Check account balance
stellar keys fund sentinel-deployer --network testnet

# Check network connection
stellar network ls
```

## 📝 Next Steps After Deployment

1. ✅ Deploy SDK contract
2. ✅ Initialize with Oracle key
3. ⏳ Build demo protocol that integrates SDK
4. ⏳ Submit test risks from Oracle
5. ⏳ Verify enforcement in demo protocol

## 🔑 Important Values

**Oracle Public Key**:
```
93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c
```

**Contract ID** (after deployment):
```
<Save your deployed contract ID here>
```

## 💡 Tips

- Keep the contract ID in a `.env` file for easy access
- Test locally with `cargo test` before deploying
- Use testnet XLM (free from faucet)
- Monitor contract events for debugging

For more details, see [README.md](./README.md)
