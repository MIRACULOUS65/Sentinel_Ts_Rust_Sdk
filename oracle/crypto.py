"""
Cryptographic operations for the Oracle service using Ed25519 signatures.

This module handles:
- Keypair generation and loading
- Payload signing with Ed25519
- Signature verification
"""

import os
import json
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_DIR = os.path.join(BASE_DIR, "keys")
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "oracle_private.key")
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "oracle_public.key")


def generate_keypair():
    """Generate a new Ed25519 keypair and save to files."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    
    # Generate new signing key
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Save private key
    with open(PRIVATE_KEY_FILE, "w") as f:
        f.write(signing_key.encode(encoder=HexEncoder).decode('utf-8'))
    
    # Save public key
    with open(PUBLIC_KEY_FILE, "w") as f:
        f.write(verify_key.encode(encoder=HexEncoder).decode('utf-8'))
    
    print(f"✅ Generated new Ed25519 keypair")
    print(f"   Private key: {PRIVATE_KEY_FILE}")
    print(f"   Public key:  {PUBLIC_KEY_FILE}")
    print(f"\n🔑 Public Key (use this in Soroban contract):")
    print(f"   {verify_key.encode(encoder=HexEncoder).decode('utf-8')}")
    
    return signing_key, verify_key


def load_keys():
    """Load existing keypair from Environment Variables or files."""
    
    # Priority 1: Environment Variables (for Render/Cloud)
    env_private = os.getenv("ORACLE_PRIVATE_KEY")
    if env_private:
        signing_key = SigningKey(env_private, encoder=HexEncoder)
        verify_key = signing_key.verify_key
        return signing_key, verify_key

    # Priority 2: Files (Local Development)
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
        raise FileNotFoundError(
            f"Keypair not found. Run 'python crypto.py --generate-keys' first or set ORACLE_PRIVATE_KEY."
        )
    
    # Load private key
    with open(PRIVATE_KEY_FILE, "r") as f:
        private_hex = f.read().strip()
        signing_key = SigningKey(private_hex, encoder=HexEncoder)
    
    # Load public key
    with open(PUBLIC_KEY_FILE, "r") as f:
        public_hex = f.read().strip()
        verify_key = VerifyKey(public_hex, encoder=HexEncoder)
    
    return signing_key, verify_key


def canonical_json(data: dict) -> bytes:
    """
    Convert dict to canonical JSON bytes for signing.
    Uses sorted keys and no whitespace for deterministic output.
    """
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sign_payload(payload: dict, signing_key: SigningKey) -> str:
    """
    Sign a payload dict with Ed25519.
    
    Args:
        payload: Dict containing {wallet, risk_score, timestamp}
        signing_key: Ed25519 signing key
        
    Returns:
        Hex-encoded signature string
    """
    # Canonical JSON serialization
    message = canonical_json(payload)
    
    # Sign with Ed25519
    signed = signing_key.sign(message)
    
    # Return just the signature part (not the message)
    signature_hex = signed.signature.hex()
    
    return signature_hex


def verify_signature(payload: dict, signature_hex: str, verify_key: VerifyKey) -> bool:
    """
    Verify a signature against a payload.
    
    Args:
        payload: Dict containing {wallet, risk_score, timestamp}
        signature_hex: Hex-encoded signature
        verify_key: Ed25519 verification key
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Canonical JSON serialization
        message = canonical_json(payload)
        
        # Convert signature from hex
        signature_bytes = bytes.fromhex(signature_hex)
        
        # Verify signature
        verify_key.verify(message, signature_bytes)
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-keys":
        generate_keypair()
    else:
        print("Usage: python crypto.py --generate-keys")
        print("\nThis will generate a new Ed25519 keypair for the Oracle.")
