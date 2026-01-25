// pub const WASM: &[u8] = soroban_sdk::contractfile!(
//    file = "sentinel_sdk.wasm", sha256 =
//    "f35b8e6697ffbe8aee91b067a1f448f36659c07278a01dae433ad4c8d0296847"
// );

/// Ed25519 public key type (32 bytes)
pub type PublicKey = soroban_sdk::BytesN<32>;

/// Ed25519 signature type (64 bytes)
pub type Signature = soroban_sdk::BytesN<64>;

#[soroban_sdk::contractclient(name = "Client")]
pub trait Contract {
    fn get_risk(
        env: soroban_sdk::Env,
        wallet: soroban_sdk::Address,
    ) -> Option<RiskState>;
    fn is_frozen(env: soroban_sdk::Env, wallet: soroban_sdk::Address) -> bool;
    fn initialize(env: soroban_sdk::Env, oracle_pubkey: PublicKey);
    fn submit_risk(env: soroban_sdk::Env, payload: RiskPayload, signature: Signature);
    fn check_permission(
        env: soroban_sdk::Env,
        wallet: soroban_sdk::Address,
    ) -> RiskDecision;
    fn get_oracle_pubkey(env: soroban_sdk::Env) -> PublicKey;
}
#[soroban_sdk::contracttype(export = false)]
#[derive(Debug, Clone, Eq, PartialEq, Ord, PartialOrd)]
pub struct RiskState {
    pub decision: RiskDecision,
    pub last_updated: u64,
    pub risk_score: u32,
}
#[soroban_sdk::contracttype(export = false)]
#[derive(Debug, Clone, Eq, PartialEq, Ord, PartialOrd)]
pub struct RiskPayload {
    pub risk_score: u32,
    pub timestamp: u64,
    pub wallet: soroban_sdk::Address,
}
#[soroban_sdk::contracttype(export = false)]
#[derive(Debug, Clone, Eq, PartialEq, Ord, PartialOrd)]
pub enum RiskDecision {
    Allow,
    Limit(u32),
    Freeze,
}

