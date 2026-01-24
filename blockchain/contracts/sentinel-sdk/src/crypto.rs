//! Cryptographic verification for Oracle signatures.
//!
//! This module handles Ed25519 signature verification using Soroban's crypto primitives.
//! Implementation matches the Oracle's canonical JSON serialization format.

use soroban_sdk::{Bytes, Env, Address, symbol_short, xdr::ToXdr};
use crate::types::{RiskPayload, Signature, PublicKey};

/// Verify Ed25519 signature from Oracle
/// 
/// This function verifies that the payload was signed by the Oracle's private key.
/// The signature verification process:
/// 1. Serialize payload to canonical JSON (matching Oracle's format)
/// 2. Verify signature using Soroban's ed25519_verify
/// 
/// # Arguments
/// * `env` - Soroban environment
/// * `payload` - Risk data (wallet, score, timestamp)
/// * `signature` - 64-byte Ed25519 signature from Oracle
/// * `public_key` - 32-byte Ed25519 public key of Oracle
/// 
/// # Returns
/// * `true` if signature is valid
/// * Panics if signature is invalid (ed25519_verify panics on invalid sigs)
pub fn verify_signature(
    env: &Env,
    payload: &RiskPayload,
    signature: &Signature,
    public_key: &PublicKey,
) -> bool {
    // Serialize payload to canonical JSON matching Oracle's format
    let message = serialize_canonical_json(env, payload);
    
    // DEBUG: Emit the exact message being verified
    // This allows us to see exactly what the contract constructed
    env.events().publish(
        (symbol_short!("DBG_MSG"),),
        message.clone()
    );
    
    // Verify using ED25519
    env.crypto().ed25519_verify(public_key, &message, signature);
    
    // If we reach here, signature is valid
    true
}

/// Serialize RiskPayload to canonical JSON format (matching Oracle)
/// 
/// Format: {"risk_score":87,"timestamp":1737718800,"wallet":"GXXX..."}
/// 
/// Key points:
/// - Sorted keys (alphabetically: risk_score, timestamp, wallet)
/// - No whitespace
/// - Compact separators (, and :)
/// 
/// This MUST match exactly what the Oracle signs in Python:
/// ```python
/// json.dumps(data, sort_keys=True, separators=(',', ':'))
/// ```
/// 
/// NOTE: This is a simplified implementation that works for test addresses.
/// For production, wallet address serialization may need adjustment.
fn serialize_canonical_json(env: &Env, payload: &RiskPayload) -> Bytes {
    let mut result = Bytes::new(env);
    
    // Start JSON object
    result.append(&Bytes::from_slice(env, b"{"));
    
    // Field 1: "risk_score":87
    result.append(&Bytes::from_slice(env, b"\"risk_score\":"));
    append_u32_as_bytes(&mut result, env, payload.risk_score);
    
    // Separator
    result.append(&Bytes::from_slice(env, b","));
    
    // Field 2: "timestamp":1737718800
    result.append(&Bytes::from_slice(env, b"\"timestamp\":"));
    append_u64_as_bytes(&mut result, env, payload.timestamp);
    
    // Separator  
    result.append(&Bytes::from_slice(env, b","));
    
    // Field 3: "wallet":"GBXXX..."
    result.append(&Bytes::from_slice(env, b"\"wallet\":\""));    
    // Serialize wallet address - convert Address to its Stellar string representation
    append_address_as_string(&mut result, env, &payload.wallet);
    
    // Close wallet value and JSON object
    result.append(&Bytes::from_slice(env, b"\"}"));
    
    result
}

/// Serialize Stellar Address to string format
/// Converts Address to "GBXXX..." format matching Oracle's serialization
fn append_address_as_string(bytes: &mut Bytes, env: &Env, address: &Address) {
    // Convert Address to its string representation (GBXXX... format)
    let addr_str = address.to_string();
    
    // Get the actual string length (Stellar addresses are 56 characters)
    let str_len = addr_str.len();
    
    // Use XDR serialization to get bytes from Soroban String
    // XDR format for ScVal::String:
    // 4 bytes: ScVal Type Tag (e.g. ScvString)
    // 4 bytes: Length (big-endian)
    // N bytes: Content
    // Padding
    let xdr_bytes = addr_str.to_xdr(env);
    
    // Skip the first 8 bytes (Tag + Length) to get actual string content
    for i in 0..str_len {
        if let Some(b) = xdr_bytes.get(8 + i) {
            bytes.append(&Bytes::from_slice(env, &[b]));
        }
    }
}

/// Convert u32 to decimal ASCII bytes (no_std compatible)
fn append_u32_as_bytes(bytes: &mut Bytes, env: &Env, mut value: u32) {
    if value == 0 {
        bytes.append(&Bytes::from_slice(env, b"0"));
        return;
    }
    
    // Build digits in reverse
    let mut digits = [0u8; 10]; // u32 max is 10 digits
    let mut i = 0;
    
    while value > 0 {
        digits[i] = (b'0' + (value % 10) as u8);
        value /= 10;
        i += 1;
    }
    
    // Append in correct order
    while i > 0 {
        i -= 1;
        let digit_slice = [digits[i]];
        bytes.append(&Bytes::from_slice(env, &digit_slice));
    }
}

/// Convert u64 to decimal ASCII bytes (no_std compatible)
fn append_u64_as_bytes(bytes: &mut Bytes, env: &Env, mut value: u64) {
    if value == 0 {
        bytes.append(&Bytes::from_slice(env, b"0"));
        return;
    }
    
    // Build digits in reverse
    let mut digits = [0u8; 20]; // u64 max is 20 digits
    let mut i = 0;
    
    while value > 0 {
        digits[i] = (b'0' + (value % 10) as u8);
        value /= 10;
        i += 1;
    }
    
    // Append in correct order
    while i > 0 {
        i -= 1;
        let digit_slice = [digits[i]];
        bytes.append(&Bytes::from_slice(env, &digit_slice));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use soroban_sdk::{Env, Address, BytesN};
    
    #[test]
    fn test_u32_to_bytes() {
        let env = Env::default();
        let mut bytes = Bytes::new(&env);
        
        append_u32_as_bytes(&mut bytes, &env, 87);
        
        let vec = bytes.to_vec();
        assert_eq!(vec, b"87");
    }
    
    #[test]
    fn test_u64_to_bytes() {
        let env = Env::default();
        let mut bytes = Bytes::new(&env);
        
        append_u64_as_bytes(&mut bytes, &env, 1737718800);
        
        let vec = bytes.to_vec();
        assert_eq!(vec, b"1737718800");
    }
    
    #[test]
    fn test_canonical_json_structure() {
        let env = Env::default();
        
        // Create test payload
        let wallet = Address::generate(&env);
        let payload = RiskPayload {
            wallet: wallet.clone(),
            risk_score: 87,
            timestamp: 1737718800,
        };
        
        // Serialize
        let json_bytes = serialize_canonical_json(&env, &payload);
        let json_vec = json_bytes.to_vec();
        
        // Should start with {"risk_score":87
        assert_eq!(&json_vec[0..15], b"{\"risk_score\":87");
        
        // Should have timestamp
        assert!(json_vec.windows(21).any(|w| w == b",\"timestamp\":1737718800"));
        
        // Should end with "}
        assert_eq!(&json_vec[json_vec.len()-2..], b"\"}");
    }
}
