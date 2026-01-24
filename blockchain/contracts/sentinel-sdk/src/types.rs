//! Data types for the Sentinel SDK contract.
//!
//! This module defines the core data structures used by the SDK:
//! - RiskState: Wallet risk information stored on-chain
//! - RiskDecision: The decision returned to integrating protocols
//! - RiskPayload: Oracle-signed risk data


use soroban_sdk::{contracttype, Address, BytesN};

/// Decision returned to protocols about what action to take
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RiskDecision {
    /// Wallet is safe - allow all operations
    Allow,
    /// Wallet has moderate risk - limit to specified amount
    Limit(u32),
    /// Wallet is high risk - freeze all operations
    Freeze,
}

/// Complete risk state for a wallet stored on-chain
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RiskState {
    /// Risk score from 0-100
    pub risk_score: u32,
    /// Unix timestamp of last update
    pub last_updated: u64,
    /// Computed decision based on risk score
    pub decision: RiskDecision,
}

/// Payload signed by Oracle (what gets verified)
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RiskPayload {
    /// Wallet address being scored
    pub wallet: Address,
    /// Risk score from 0-100
    pub risk_score: u32,
    /// Unix timestamp when Oracle signed this
    pub timestamp: u64,
}

/// Ed25519 signature type (64 bytes)
pub type Signature = BytesN<64>;

/// Ed25519 public key type (32 bytes)
pub type PublicKey = BytesN<32>;

impl RiskState {
    /// Create new RiskState from payload
    pub fn from_payload(payload: &RiskPayload) -> Self {
        let decision = Self::calculate_decision(payload.risk_score);
        
        RiskState {
            risk_score: payload.risk_score,
            last_updated: payload.timestamp,
            decision,
        }
    }
    
    /// Calculate decision from risk score (deterministic)
    fn calculate_decision(risk_score: u32) -> RiskDecision {
        match risk_score {
            0..=49 => RiskDecision::Allow,
            50..=79 => RiskDecision::Limit(5000), // 5000 stroops limit
            80..=100 => RiskDecision::Freeze,
            _ => panic!("Invalid risk score: must be 0-100"),
        }
    }
}
