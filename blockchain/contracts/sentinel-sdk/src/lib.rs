#![no_std]

/*!
# Sentinel SDK - On-Chain Risk Enforcement for Stellar

Sentinel SDK is a **programmable risk-enforcement infrastructure** for Stellar protocols.
It provides AI-verified risk decisions that any protocol can integrate.

## What This SDK Does

- ✅ Stores wallet risk scores on-chain (Oracle-signed)
- ✅ Provides risk decisions to integrating protocols
- ✅ Verifies Ed25519 signatures from Oracle
- ✅ Emits events for observability

## What This SDK Does NOT Do

- ❌ Does NOT enforce directly
- ❌ Does NOT freeze Stellar accounts
- ❌ Does NOT control user funds

## Integration Example

```rust
use sentinel_sdk::{SentinelClient, RiskDecision};

let sentinel = SentinelClient::new(&env, sentinel_contract_id);
let decision = sentinel.check_permission(user_wallet);

match decision {
    RiskDecision::Allow => proceed_with_transaction(),
    RiskDecision::Limit(max) => enforce_limit(max),
    RiskDecision::Freeze => panic!("Blocked by Sentinel"),
}
```

## Architecture

```
ML Engine → Oracle (Ed25519 Sign) → Sentinel SDK → Protocols
                                          ↓
                                    [Provides Decisions]
                                          ↓
                                    Protocols Enforce
```
*/

use soroban_sdk::{contract, contractimpl, symbol_short, Address, Env};

mod types;
mod crypto;

use types::{RiskState, RiskDecision, RiskPayload, Signature, PublicKey};
use crypto::verify_signature;



/// Sentinel SDK Contract
#[contract]
pub struct SentinelSDK;

#[contractimpl]
impl SentinelSDK {
    
    /// Initialize the SDK with Oracle's public key
    /// 
    /// This must be called once after deployment.
    /// The Oracle public key is immutable after initialization.
    /// 
    /// # Arguments
    /// * `oracle_pubkey` - Ed25519 public key from Oracle service
    /// 
    /// # Panics
    /// * If already initialized
    pub fn initialize(env: Env, oracle_pubkey: PublicKey) {
        let storage = env.storage().instance();
        
        // Check if already initialized
        if storage.has(&symbol_short!("oracle")) {
            panic!("SDK already initialized");
        }
        
        // Store Oracle public key
        storage.set(&symbol_short!("oracle"), &oracle_pubkey);
        
        // Emit initialization event
        env.events().publish(
            (symbol_short!("SDK_INIT"),),
            oracle_pubkey
        );
    }
    
    /// Submit signed risk score from Oracle
    /// 
    /// Only the Oracle can call this (verified by signature).
    /// Updates the on-chain risk state for a wallet.
    /// 
    /// # Arguments
    /// * `payload` - Risk data (wallet, score, timestamp)
    /// * `signature` - Ed25519 signature from Oracle
    /// 
    /// # Panics
    /// * If signature is invalid
    /// * If timestamp is too old (>5 minutes)
    /// * If risk score is out of range (0-100)
    pub fn submit_risk(
        env: Env,
        payload: RiskPayload,
        signature: Signature,
    ) {
        // 1. Get Oracle public key
        let oracle_pubkey = Self::get_oracle_pubkey(&env);
        
        // 2. Verify signature
        if !verify_signature(&env, &payload, &signature, &oracle_pubkey) {
            panic!("Invalid Oracle signature");
        }
        
        // 3. Check timestamp freshness (prevent replay attacks)
        let current_time = env.ledger().timestamp();
        let max_age: u64 = 300; // 5 minutes
        
        if current_time > payload.timestamp && (current_time - payload.timestamp) > max_age {
            panic!("Payload too old - potential replay attack");
        }
        
        // 4. Validate risk score
        if payload.risk_score > 100 {
            panic!("Invalid risk score: must be 0-100");
        }
        
        // 5. Create and store risk state
        let risk_state = RiskState::from_payload(&payload);
        env.storage().persistent().set(&payload.wallet, &risk_state);
        
        // 6. Emit events based on decision
        env.events().publish(
            (symbol_short!("RISK_UPD"),),
            (payload.wallet.clone(), payload.risk_score, payload.timestamp)
        );
        
        match risk_state.decision {
            RiskDecision::Freeze => {
                env.events().publish(
                    (symbol_short!("FROZEN"),),
                    (payload.wallet.clone(), payload.risk_score)
                );
            },
            RiskDecision::Limit(limit) => {
                env.events().publish(
                    (symbol_short!("LIMITED"),),
                    (payload.wallet.clone(), payload.risk_score, limit)
                );
            },
            RiskDecision::Allow => {
                env.events().publish(
                    (symbol_short!("ALLOWED"),),
                    (payload.wallet.clone(), payload.risk_score)
                );
            }
        }
    }
    
    /// Query risk state for a wallet (read-only)
    /// 
    /// Any contract can call this to check a wallet's risk status.
    /// Returns None if wallet has never been scored.
    /// 
    /// # Arguments
    /// * `wallet` - Address to query
    /// 
    /// # Returns
    /// * `Some(RiskState)` if wallet has been scored
    /// * `None` if wallet is unknown (treat as Allow)
    pub fn get_risk(env: Env, wallet: Address) -> Option<RiskState> {
        env.storage().persistent().get(&wallet)
    }
    
    /// Check permission decision for a wallet (SDK core function)
    /// 
    /// This is the main function integrating protocols call.
    /// Returns the risk decision without enforcing it.
    /// 
    /// # Arguments
    /// * `wallet` - Address to check
    /// 
    /// # Returns
    /// * `RiskDecision` - Allow, Limit(amount), or Freeze
    /// 
    /// # Default Behavior
    /// * If wallet is unknown, returns `Allow` (innocent until proven risky)
    pub fn check_permission(env: Env, wallet: Address) -> RiskDecision {
        match Self::get_risk(env, wallet.clone()) {
            Some(risk_state) => risk_state.decision,
            None => RiskDecision::Allow, // Unknown wallets are allowed
        }
    }
    
    /// Check if wallet is frozen (convenience function)
    /// 
    /// # Arguments
    /// * `wallet` - Address to check
    /// 
    /// # Returns
    /// * `true` if wallet is frozen
    /// * `false` otherwise
    pub fn is_frozen(env: Env, wallet: Address) -> bool {
        matches!(
            Self::check_permission(env, wallet),
            RiskDecision::Freeze
        )
    }
    
    /// Get Oracle's public key (read-only)
    /// 
    /// Returns the Ed25519 public key used to verify Oracle signatures.
    /// 
    /// # Returns
    /// * Oracle's public key
    /// 
    /// # Panics
    /// * If SDK not initialized
    pub fn get_oracle_pubkey(env: &Env) -> PublicKey {
        env.storage()
            .instance()
            .get(&symbol_short!("oracle"))
            .expect("SDK not initialized - call initialize() first")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use soroban_sdk::{Env, BytesN};
    
    #[test]
    fn test_initialize() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SentinelSDK);
        let client = SentinelSDKClient::new(&env, &contract_id);
        
        // Generate test Oracle key
        let oracle_key = BytesN::from_array(&env, &[0u8; 32]);
        
        // Initialize
        client.initialize(&oracle_key);
        
        // Verify Oracle key is stored
        let stored_key = client.get_oracle_pubkey();
        assert_eq!(stored_key, oracle_key);
    }
    
    #[test]
    #[should_panic(expected = "SDK already initialized")]
    fn test_double_initialization() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SentinelSDK);
        let client = SentinelSDKClient::new(&env, &contract_id);
        
        let oracle_key = BytesN::from_array(&env, &[0u8; 32]);
        
        // First initialization
        client.initialize(&oracle_key);
        
        // Second initialization should panic
        client.initialize(&oracle_key);
    }
    
    #[test]
    fn test_unknown_wallet_is_allowed() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SentinelSDK);
        let client = SentinelSDKClient::new(&env, &contract_id);
        
        // Initialize SDK
        let oracle_key = BytesN::from_array(&env, &[0u8; 32]);
        client.initialize(&oracle_key);
        
        // Check unknown wallet
        let unknown_wallet = Address::generate(&env);
        let decision = client.check_permission(&unknown_wallet);
        
        // Should default to Allow
        assert_eq!(decision, RiskDecision::Allow);
    }
    
    #[test]
    fn test_is_frozen() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SentinelSDK);
        let client = SentinelSDKClient::new(&env, &contract_id);
        
        // Initialize SDK
        let oracle_key = BytesN::from_array(&env, &[0u8; 32]);
        client.initialize(&oracle_key);
        
        // Unknown wallet should not be frozen
        let wallet = Address::generate(&env);
        assert_eq!(client.is_frozen(&wallet), false);
    }
}
