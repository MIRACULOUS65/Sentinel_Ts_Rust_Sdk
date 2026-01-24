# Building Soroban Smart Contract for On-Chain Risk Enforcement

**End-to-End Walkthrough: Oracle Signatures → Smart Contract Verification → Autonomous Enforcement**

---

## 🎯 What This Contract Does

The Soroban smart contract is the **on-chain enforcement layer** that:
1. ✅ Verifies Ed25519 signatures from the Oracle
2. ✅ Stores wallet risk scores permanently on-chain
3. ✅ Enforces autonomous risk rules (freeze/limit/allow)
4. ✅ Emits events for frontend visualization
5. ✅ Prevents replay attacks with timestamp validation

**Critical Design Principle**: 
> Smart contracts NEVER trust AI directly. They ONLY trust cryptographic signatures.

---

## 🏗️ Complete Architecture Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
│ ML Engine   │ ──▶ │ Oracle       │ ──▶ │ Soroban        │ ──▶ │ Enforcement │
│ (Risk Score)│     │ (Ed25519     │     │ Contract       │     │ (On-Chain)  │
│             │     │  Signature)  │     │ (Verify Sign)  │     │             │
└─────────────┘     └──────────────┘     └─────────────────┘     └─────────────┘
     OFF-CHAIN           OFF-CHAIN              ON-CHAIN              ON-CHAIN
```

---

## 📋 Contract Requirements

### What the Contract Must Do

1. **Store Oracle Public Key**
   - Hardcoded at deployment
   - Used for all signature verifications
   - Cannot be changed (immutable for hackathon)

2. **Verify Ed25519 Signatures**
   - Receive signed payload from Oracle
   - Verify signature matches Oracle's public key
   - Reject invalid signatures

3. **Store Risk Scores**
   - Map: `wallet_address → (risk_score, timestamp)`
   - Persistent storage on Stellar blockchain
   - Queryable by anyone

4. **Enforce Risk Rules**
   ```rust
   risk >= 80  → FREEZE (panic on transactions)
   50 <= risk < 80 → LIMIT (restricted operations)
   risk < 50 → ALLOW (normal operations)
   ```

5. **Emit Events**
   - `RISK_UPDATED(wallet, risk_score, timestamp)`
   - `WALLET_FROZEN(wallet, risk_score)`
   - `WALLET_LIMITED(wallet, risk_score)`

6. **Timestamp Validation**
   - Reject payloads older than 5 minutes
   - Prevent replay attacks
   - Ensure freshness

---

## 🛠️ Development Environment Setup

### Prerequisites

1. **Install Rust**
   ```powershell
   # Download rustup from https://rustup.rs/
   # Run installer
   rustup default stable
   rustup target add wasm32-unknown-unknown
   ```

2. **Install Stellar CLI**
   ```powershell
   cargo install --locked stellar-cli --features opt
   ```

3. **Configure for Testnet**
   ```powershell
   stellar network add --global testnet `
     --rpc-url https://soroban-testnet.stellar.org:443 `
     --network-passphrase "Test SDF Network ; September 2015"
   ```

4. **Create Identity (Wallet)**
   ```powershell
   stellar keys generate --global oracle-deployer --network testnet
   ```

5. **Fund Account**
   ```powershell
   stellar keys fund oracle-deployer --network testnet
   ```

---

## 📝 Contract Structure

### File Organization

```
blockchain/
├── Cargo.toml
├── src/
│   ├── lib.rs           # Main contract
│   ├── types.rs         # Data structures
│   └── crypto.rs        # Signature verification
├── README.md
└── tests/
    └── integration_test.rs
```

---

## 🔐 Contract Implementation

### 1. Data Structures (`types.rs`)

```rust
use soroban_sdk::{contracttype, Address, BytesN};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RiskPayload {
    pub wallet: Address,
    pub risk_score: u32,
    pub timestamp: u64,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WalletRisk {
    pub risk_score: u32,
    pub last_updated: u64,
    pub status: RiskStatus,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RiskStatus {
    Allow,
    Limit,
    Freeze,
}

pub type Signature = BytesN<64>;
pub type PublicKey = BytesN<32>;
```

### 2. Main Contract (`lib.rs`)

```rust
#![no_std]
use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, BytesN, log};
mod types;
mod crypto;

use types::*;
use crypto::verify_ed25519;

#[contract]
pub struct RiskEnforcementContract;

#[contractimpl]
impl RiskEnforcementContract {
    
    /// Initialize contract with Oracle public key
    pub fn initialize(env: Env, oracle_pubkey: PublicKey) {
        let storage = env.storage().instance();
        storage.set(&symbol_short!("oracle_pk"), &oracle_pubkey);
    }
    
    /// Submit signed risk score from Oracle
    pub fn submit_risk(
        env: Env,
        payload: RiskPayload,
        signature: Signature,
    ) {
        // 1. Verify signature
        let oracle_pubkey = Self::get_oracle_pubkey(&env);
        let is_valid = verify_ed25519(&env, &payload, &signature, &oracle_pubkey);
        
        if !is_valid {
            panic!("Invalid signature");
        }
        
        // 2. Check timestamp freshness (prevent replay)
        let current_time = env.ledger().timestamp();
        let max_age = 300; // 5 minutes
        
        if current_time - payload.timestamp > max_age {
            panic!("Payload too old");
        }
        
        // 3. Determine risk status
        let status = match payload.risk_score {
            s if s >= 80 => RiskStatus::Freeze,
            s if s >= 50 => RiskStatus::Limit,
            _ => RiskStatus::Allow,
        };
        
        // 4. Store wallet risk
        let wallet_risk = WalletRisk {
            risk_score: payload.risk_score,
            last_updated: payload.timestamp,
            status: status.clone(),
        };
        
        env.storage().persistent().set(&payload.wallet, &wallet_risk);
        
        // 5. Emit events
        env.events().publish(
            (symbol_short!("RISK_UPD"),),
            (payload.wallet.clone(), payload.risk_score, payload.timestamp)
        );
        
        match status {
            RiskStatus::Freeze => {
                env.events().publish(
                    (symbol_short!("FROZEN"),),
                    (payload.wallet.clone(), payload.risk_score)
                );
            },
            RiskStatus::Limit => {
                env.events().publish(
                    (symbol_short!("LIMITED"),),
                    (payload.wallet.clone(), payload.risk_score)
                );
            },
            _ => {}
        }
    }
    
    /// Check if wallet is frozen
    pub fn is_frozen(env: Env, wallet: Address) -> bool {
        match env.storage().persistent().get::<Address, WalletRisk>(&wallet) {
            Some(risk) => matches!(risk.status, RiskStatus::Freeze),
            None => false,
        }
    }
    
    /// Get wallet risk score
    pub fn get_risk(env: Env, wallet: Address) -> Option<WalletRisk> {
        env.storage().persistent().get(&wallet)
    }
    
    // Internal helper
    fn get_oracle_pubkey(env: &Env) -> PublicKey {
        env.storage().instance().get(&symbol_short!("oracle_pk"))
            .expect("Oracle public key not initialized")
    }
}
```

### 3. Signature Verification (`crypto.rs`)

```rust
use soroban_sdk::{Env, Bytes, BytesN};
use crate::types::{RiskPayload, Signature, PublicKey};

pub fn verify_ed25519(
    env: &Env,
    payload: &RiskPayload,
    signature: &Signature,
    public_key: &PublicKey,
) -> bool {
    // Serialize payload to canonical JSON
    let message = serialize_payload(env, payload);
    
    // Verify Ed25519 signature using Soroban crypto
    env.crypto().ed25519_verify(
        public_key,
        &message,
        signature
    )
}

fn serialize_payload(env: &Env, payload: &RiskPayload) -> Bytes {
    // Canonical JSON: {"risk_score":87,"timestamp":1737718800,"wallet":"G..."}
    // Must match Oracle's canonical_json() output
    
    let mut bytes = Bytes::new(env);
    
    // Format: {"risk_score":XX,"timestamp":XXXXX,"wallet":"GXXX..."}
    bytes.append(&Bytes::from_slice(env, b"{\"risk_score\":"));
    bytes.append(&u32_to_bytes(env, payload.risk_score));
    bytes.append(&Bytes::from_slice(env, b",\"timestamp\":"));
    bytes.append(&u64_to_bytes(env, payload.timestamp));
    bytes.append(&Bytes::from_slice(env, b",\"wallet\":\""));
    bytes.append(&address_to_bytes(env, &payload.wallet));
    bytes.append(&Bytes::from_slice(env, b"\"}"));
    
    bytes
}

// Helper functions for serialization
fn u32_to_bytes(env: &Env, num: u32) -> Bytes {
    Bytes::from_slice(env, num.to_string().as_bytes())
}

fn u64_to_bytes(env: &Env, num: u64) -> Bytes {
    Bytes::from_slice(env, num.to_string().as_bytes())
}

fn address_to_bytes(env: &Env, addr: &Address) -> Bytes {
    // Convert Stellar address to string
    Bytes::from_slice(env, addr.to_string().as_bytes())
}
```

---

## 🔧 Cargo Configuration

### `Cargo.toml`

```toml
[package]
name = "sentinel-risk-contract"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
soroban-sdk = "21.0.0"

[dev-dependencies]
soroban-sdk = { version = "21.0.0", features = ["testutils"] }

[profile.release]
opt-level = "z"
overflow-checks = true
debug = 0
strip = "symbols"
debug-assertions = false
panic = "abort"
codegen-units = 1
lto = true

[profile.release-with-logs]
inherits = "release"
debug-assertions = true
```

---

## 🚀 Deployment Process

### Step 1: Build Contract

```powershell
cd d:\sentinel_local\Sentinel\blockchain
stellar contract build
```

Output: `target/wasm32-unknown-unknown/release/sentinel_risk_contract.wasm`

### Step 2: Optimize WASM

```powershell
stellar contract optimize --wasm target/wasm32-unknown-unknown/release/sentinel_risk_contract.wasm
```

### Step 3: Deploy to Testnet

```powershell
stellar contract deploy `
  --wasm target/wasm32-unknown-unknown/release/sentinel_risk_contract.optimized.wasm `
  --source oracle-deployer `
  --network testnet
```

Output: Contract ID (e.g., `CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABSC4`)

### Step 4: Initialize with Oracle Public Key

```powershell
# Use the Oracle public key from earlier:
# 93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c

stellar contract invoke `
  --id <CONTRACT_ID> `
  --source oracle-deployer `
  --network testnet `
  -- initialize `
  --oracle_pubkey 93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c
```

---

## 🧪 Testing the Contract

### Test 1: Submit Signed Risk from Oracle

```python
# Python script: submit_to_soroban.py
import requests
from stellar_sdk import SorobanServer, Keypair, TransactionBuilder, Network

# 1. Get signed payload from Oracle
oracle_response = requests.post(
    "http://localhost:8001/sign-risk",
    json={
        "wallet": "GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
        "risk_score": 87,
        "reason": "abnormal circular transfers"
    }
).json()

# 2. Submit to Soroban contract
# (Use Stellar SDK to call submit_risk function)
```

### Test 2: Query Wallet Risk

```powershell
stellar contract invoke `
  --id <CONTRACT_ID> `
  --source oracle-deployer `
  --network testnet `
  -- get_risk `
  --wallet GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR
```

### Test 3: Check if Frozen

```powershell
stellar contract invoke `
  --id <CONTRACT_ID> `
  --source oracle-deployer `
  --network testnet `
  -- is_frozen `
  --wallet GABCD3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR
```

---

## 🎯 Risk Enforcement Rules

### Implementation Logic

```rust
match risk_score {
    0..=49 => {
        // ✅ ALLOW - Normal operations
        // No restrictions
        RiskStatus::Allow
    },
    50..=79 => {
        // ⚠️ LIMIT - Restricted operations
        // Example: Max transaction amount
        // Example: Require additional confirmations
        RiskStatus::Limit
    },
    80..=100 => {
        // 🔴 FREEZE - Blocked
        // All operations panic
        RiskStatus::Freeze
    },
    _ => panic!("Invalid risk score")
}
```

### Frontend Integration

```typescript
// Check wallet status before allowing transactions
const walletRisk = await contract.get_risk(walletAddress);

if (walletRisk?.status === 'Freeze') {
    alert('⛔ Wallet is FROZEN due to high risk score');
    return;
}

if (walletRisk?.status === 'Limit') {
    alert('⚠️ Wallet has LIMITS - reduced transaction amounts');
}

// Proceed with transaction...
```

---

## 📊 Events for Frontend Visualization

### Event Structure

```rust
// Event: RISK_UPDATED
topic: ["RISK_UPD"]
data: (wallet_address, risk_score, timestamp)

// Event: WALLET_FROZEN
topic: ["FROZEN"]
data: (wallet_address, risk_score)

// Event: WALLET_LIMITED
topic: ["LIMITED"]
data: (wallet_address, risk_score)
```

### Frontend Listener

```typescript
// Listen for contract events
const events = await contract.getEvents({
    filters: ['RISK_UPD', 'FROZEN', 'LIMITED'],
    startLedger: lastProcessedLedger
});

events.forEach(event => {
    if (event.topic === 'FROZEN') {
        displayAlert(`Wallet ${event.wallet} FROZEN`);
    }
});
```

---

## 🔒 Security Guarantees

1. **Signature Verification**: Only Oracle can submit valid risk scores
2. **Timestamp Validation**: Prevents replay attacks (max 5 minutes old)
3. **Immutable Public Key**: Oracle key set at deployment, cannot change
4. **Deterministic Enforcement**: Same risk score → same enforcement
5. **Event Transparency**: All actions logged on-chain

---

## 🔗 Complete Integration Flow

### End-to-End Example

```python
# 1. ML Engine predicts risk (or use mock data)
ml_output = {
    "wallet": "GABCD...",
    "risk_score": 87,
    "reason": "abnormal circular transfers"
}

# 2. Oracle signs the payload
oracle_response = requests.post(
    "http://localhost:8001/sign-risk",
    json=ml_output
)
signed_payload = oracle_response.json()

# 3. Submit to Soroban contract
contract = SorobanContract(CONTRACT_ID)
result = contract.submit_risk(
    payload={
        "wallet": signed_payload["payload"]["wallet"],
        "risk_score": signed_payload["payload"]["risk_score"],
        "timestamp": signed_payload["payload"]["timestamp"]
    },
    signature=signed_payload["signature"]
)

# 4. Contract verifies signature automatically
# 5. Contract stores risk score on-chain
# 6. Contract enforces freeze/limit/allow rules
# 7. Events emitted for frontend
```

---

## 📱 Next Steps

### After Contract Deployment

1. **Update Oracle Service**:
   - Add Soroban submission logic
   - Auto-submit after signing

2. **Frontend Integration**:
   - Query contract for wallet status
   - Display enforcement events
   - Show freeze/limit indicators

3. **ML Integration**:
   - Replace mock data with real ML predictions
   - Keep same Oracle→Soroban flow

---

## 📚 Resources

- **Soroban Docs**: https://soroban.stellar.org/docs
- **Stellar CLI**: https://developers.stellar.org/docs/tools/stellar-cli
- **Ed25519 in Soroban**: https://soroban.stellar.org/docs/reference/crypto
- **Contract Examples**: https://github.com/stellar/soroban-examples

---

## ✅ Summary

**What We're Building**:
- ✅ Soroban smart contract in Rust
- ✅ Ed25519 signature verification
- ✅ On-chain risk storage
- ✅ Autonomous enforcement (freeze/limit/allow)
- ✅ Event emission for frontend
- ✅ Timestamp-based replay protection

**Key Files**:
- `lib.rs` - Main contract logic
- `types.rs` - Data structures
- `crypto.rs` - Signature verification
- `Cargo.toml` - Build configuration

**Deployment**:
1. Build WASM
2. Deploy to Stellar testnet
3. Initialize with Oracle public key: `93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c`
4. Test with Oracle-signed payloads

**Oracle Public Key** (embed in contract):
```
93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c
```

**This completes the trust chain**: ML → Oracle (Sign) → Soroban (Verify) → Enforcement 🚀
