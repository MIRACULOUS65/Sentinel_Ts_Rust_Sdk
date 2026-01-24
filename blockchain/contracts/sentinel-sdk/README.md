# Sentinel SDK - Soroban Smart Contract

On-chain risk enforcement SDK for Stellar protocols.

## 🎯 What This Is

Sentinel SDK is **infrastructure**, not an application. It provides AI-verified risk decisions that any Stellar protocol can integrate.

**Think of it like**:
- Chainlink (but for risk instead of price data)
- An on-chain risk API
- Programmable fraud prevention

## 🏗️ Architecture

```
ML Engine → Oracle (Ed25519) → Sentinel SDK Contract
                                        ↓
                            [Provides Risk Decisions]
                                        ↓
                    ┌───────────────────┼───────────────┐
                    ↓                   ↓               ↓
                  AMM              Lending          Payment
               Protocol            Protocol           App
```

**Key Principle**: Sentinel decides, protocols enforce.

## 📦 Core Functions

### For Protocols (Integrators)

```rust
// Check permission for a wallet
pub fn check_permission(wallet: Address) -> RiskDecision

// Get full risk state
pub fn get_risk(wallet: Address) -> Option<RiskState>

// Quick freeze check
pub fn is_frozen(wallet: Address) -> bool
```

### For Oracle (Restricted)

```rust
// Submit signed risk score
pub fn submit_risk(payload: RiskPayload, signature: Signature)
```

### For Setup

```rust
// One-time initialization
pub fn initialize(oracle_pubkey: PublicKey)
```

## 🔑 Risk Decision Types

```rust
enum RiskDecision {
    Allow,           // Safe - proceed normally
    Limit(u32),      // Moderate risk - enforce limit
    Freeze,          // High risk - block operation
}
```

## 📋 Integration Example

```rust
use sentinel_sdk::SentinelSDKClient;

// In your protocol's contract
let sentinel = SentinelSDKClient::new(&env, &sentinel_contract_id);

match sentinel.check_permission(&user_wallet) {
    RiskDecision::Allow => {
        // Proceed with transaction
        self.execute_transfer(from, to, amount)
    },
    RiskDecision::Limit(max_amount) => {
        if amount > max_amount {
            panic!("Transaction exceeds risk limit");
        }
        self.execute_transfer(from, to, amount)
    },
    RiskDecision::Freeze => {
        panic!("Wallet blocked by Sentinel risk engine");
    }
}
```

## 🛠️ Building

```bash
# Build contract
cargo build --target wasm32-unknown-unknown --release

# Or use Stellar CLI
stellar contract build
```

## 🚀 Deployment

```bash
# Deploy to testnet
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/sentinel_sdk.wasm \
  --source deployer \
  --network testnet

# Initialize with Oracle public key
stellar contract invoke \
  --id <CONTRACT_ID> \
  --source deployer \
  --network testnet \
  -- initialize \
  --oracle_pubkey 93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c
```

## 🧪 Testing

```bash
cargo test
```

## 📊 Events Emitted

| Event | When | Data |
|-------|------|------|
| `SDK_INIT` | Initialization | Oracle public key |
| `RISK_UPD` | Risk updated | (wallet, risk_score, timestamp) |
| `FROZEN` | Wallet frozen | (wallet, risk_score) |
| `LIMITED` | Wallet limited | (wallet, risk_score, limit) |
| `ALLOWED` | Wallet allowed | (wallet, risk_score) |

## 🔐 Security Model

1. **Oracle Authority**: Only Oracle can submit risk scores (verified by Ed25519)
2. **Replay Protection**: Timestamps must be fresh (<5 minutes)
3. **Immutable Oracle Key**: Cannot be changed after initialization
4. **Deterministic Decisions**: Same risk score always gives same decision

## 📝 Data Structures

### RiskState
```rust
struct RiskState {
    risk_score: u32,      // 0-100
    last_updated: u64,    // Unix timestamp
    decision: RiskDecision,
}
```

### RiskPayload (Oracle-signed)
```rust
struct RiskPayload {
    wallet: Address,
    risk_score: u32,
    timestamp: u64,
}
```

## 🎯 Decision Logic

```rust
match risk_score {
    0..=49   => RiskDecision::Allow,
    50..=79  => RiskDecision::Limit(5000),  // 5000 stroops
    80..=100 => RiskDecision::Freeze,
}
```

## 🚫 What This SDK Does NOT Do

- ❌ Does NOT freeze Stellar accounts globally
- ❌ Does NOT control user funds
- ❌ Does NOT enforce automatically
- ❌ Does NOT require integration

**Enforcement is OPT-IN** - protocols choose to integrate.

## 📚 Learn More

- **Oracle Service**: `../../oracle/README.md`
- **Integration Guide**: `../../docs/INTEGRATION.md` (coming soon)
- **Architecture**: `../../blockchain.md`

## 🤝 For Developers

To integrate Sentinel SDK into your protocol:

1. Add SDK contract ID to your contract
2. Call `check_permission(wallet)` before operations
3. Handle the returned `RiskDecision`
4. Deploy and test!

That's it! Your protocol now has AI-verified fraud prevention.

## 📄 License

MIT
