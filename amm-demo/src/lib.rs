#![no_std]
use soroban_sdk::{contract, contractimpl, contracttype, symbol_short, Address, Env, Symbol};

// 1. Define the enum exactly as it is in the Sentinel SDK
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RiskDecision {
    Allow,
    Limit(u32),
    Freeze,
}

// 2. Define the client interface for calling Sentinel
// We don't strictly need the trait if we just use env.invoke_contract, 
// but let's use a helper for cleaner code.
pub struct SentinelClient<'a> {
    env: &'a Env,
    contract_id: Address,
}

impl<'a> SentinelClient<'a> {
    pub fn new(env: &'a Env, contract_id: &Address) -> Self {
        Self {
            env,
            contract_id: contract_id.clone(),
        }
    }

    pub fn check_permission(&self, wallet: &Address) -> RiskDecision {
        self.env.invoke_contract(
            &self.contract_id,
            &Symbol::new(&self.env, "check_permission"), 
            soroban_sdk::vec![&self.env, wallet.to_val()],
        )
    }
}

#[contract]
pub struct MockAMM;

#[contractimpl]
impl MockAMM {
    pub fn initialize(env: Env, sentinel_id: Address) {
        env.storage().instance().set(&symbol_short!("sentinel"), &sentinel_id);
    }

    pub fn swap(env: Env, user: Address, amount: i128) -> Symbol {
        let sentinel_id: Address = env.storage().instance().get(&symbol_short!("sentinel"))
            .expect("AMM not initialized");
        
        // Manual invoke to avoid client gen issues
        // "check_permission" is longer than 9 chars, so we use Symbol::new
        let decision: RiskDecision = env.invoke_contract(
            &sentinel_id,
            &Symbol::new(&env, "check_permission"), 
            soroban_sdk::vec![&env, user.to_val()]
        );
        
        match decision {
            RiskDecision::Allow => {
                env.events().publish((symbol_short!("SWAP"),), (user, amount, "SUCCESS"));
                symbol_short!("SUCCESS")
            },
            RiskDecision::Limit(limit) => {
                if amount > (limit as i128) {
                     env.events().publish((symbol_short!("SWAP"),), (user, amount, "BLOCKED_LIMIT"));
                     panic!("Swap blocked: Amount exceeds risk limit");
                } else {
                     env.events().publish((symbol_short!("SWAP"),), (user, amount, "WARN_LIMIT"));
                     symbol_short!("WARNING") 
                }
            },
            RiskDecision::Freeze => {
                env.events().publish((symbol_short!("SWAP"),), (user, amount, "BLOCKED_FRZ"));
                panic!("Swap blocked: Account is frozen by Sentinel");
            }
        }
    }
}
