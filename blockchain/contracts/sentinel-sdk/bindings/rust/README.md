# Sentinel SDK - Rust Bindings

Rust client bindings for the Sentinel SDK smart contract.

## Usage

Add to your `Cargo.toml`:

```toml
[dependencies]
soroban-sdk = "21.0.0"
```

Include the bindings in your contract:

```rust
mod sentinel_sdk {
    include!("path/to/bindings/rust/lib.rs");
}

use sentinel_sdk::{Client as SentinelClient, RiskDecision};
```

## Example: Integrating in Another Contract

```rust
use soroban_sdk::{contract, contractimpl, Address, Env};

mod sentinel_sdk {
    include!("bindings/rust/lib.rs");
}

#[contract]
pub struct MyProtocol;

#[contractimpl]
impl MyProtocol {
    pub fn transfer(
        env: Env,
        from: Address,
        to: Address,
        amount: i128
    ) -> Result<(), Error> {
        // Initialize Sentinel SDK client
        let sentinel_contract_id = Address::from_string(
            &env.string_from_bytes(&env.bytes_from_slice(
                b"CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO"
            ))
        );
        let sentinel = sentinel_sdk::Client::new(&env, &sentinel_contract_id);
        
        // Check permission
        let decision = sentinel.check_permission(&from);
        
        // Enforce based on decision
        match decision {
            sentinel_sdk::RiskDecision::Allow => {
                // Proceed with transfer
                Self::do_transfer(env, from, to, amount)
            },
            sentinel_sdk::RiskDecision::Limit(max_amount) => {
                if amount > max_amount as i128 {
                    panic!("Transaction exceeds limit for risky wallet");
                }
                Self::do_transfer(env, from, to, amount)
            },
            sentinel_sdk::RiskDecision::Freeze => {
                panic!("Wallet is frozen by Sentinel risk engine");
            }
        }
    }
    
    fn do_transfer(
        env: Env,
        from: Address,
        to: Address,
        amount: i128
    ) -> Result<(), Error> {
        // Your transfer logic here
        Ok(())
    }
}
```

## Available Types

### RiskDecision
```rust
pub enum RiskDecision {
    Allow,
    Limit(u32),
    Freeze,
}
```

### RiskState
```rust
pub struct RiskState {
    pub decision: RiskDecision,
    pub last_updated: u64,
    pub risk_score: u32,
}
```

### RiskPayload
```rust
pub struct RiskPayload {
    pub risk_score: u32,
    pub timestamp: u64,
    pub wallet: soroban_sdk::Address,
}
```

## Client Methods

```rust
impl Client {
    // Check wallet permission (main SDK function)
    fn check_permission(
        env: Env,
        wallet: Address
    ) -> RiskDecision;
    
    // Get full risk state
    fn get_risk(
        env: Env,
        wallet: Address
    ) -> Option<RiskState>;
    
    // Quick freeze check
    fn is_frozen(
        env: Env,
        wallet: Address
    ) -> bool;
    
    // Initialize (one-time)
    fn initialize(
        env: Env,
        oracle_pubkey: PublicKey
    );
    
    // Submit risk (Oracle only)
    fn submit_risk(
        env: Env,
        payload: RiskPayload,
        signature: Signature
    );
    
    // Get Oracle public key
    fn get_oracle_pubkey(env: Env) -> PublicKey;
}
```

## Contract ID

**Testnet**: `CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO`

## WASM Hash

The bindings include the embedded WASM hash for verification:
```
f35b8e6697ffbe8aee91b067a1f448f36659c07278a01dae433ad4c8d0296847
```
