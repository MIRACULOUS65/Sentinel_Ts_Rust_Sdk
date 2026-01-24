# Sentinel SDK - Contract Bindings Guide

Contract bindings have been generated for the deployed Sentinel SDK contract.

## 📦 TypeScript Bindings

**Location**: `bindings/typescript/`

**Contract ID**: `CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO`

### Setup

```bash
cd bindings/typescript
npm install
npm run build
```

### Usage Example

```typescript
import { Contract as SentinelSDK } from './bindings/typescript';
import { Server } from '@stellar/stellar-sdk';

// Initialize SDK client
const server = new Server('https://soroban-testnet.stellar.org');
const contractId = 'CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO';
const sdk = new SentinelSDK({ contractId, networkPassphrase, server });

// Check wallet permission
const decision = await sdk.check_permission({ wallet: 'GABCD...' });

// decision will be: { tag: 'Allow' } | { tag: 'Limit', value: number } | { tag:'Freeze' }

if (decision.tag === 'Freeze') {
  console.log('⛔ Wallet is frozen');
} else if (decision.tag === 'Limit') {
  console.log(`⚠️ Wallet limited to ${decision.value}`);
} else {
  console.log('✅ Wallet allowed');
}
```

### Initialize Contract

```typescript
// Initialize with Oracle public key
const oracleKey = Buffer.from('93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c', 'hex');

await sdk.initialize({
  oracle_pubkey: oracleKey
}, {
  // Transaction options
  fee: '100',
  networkPassphrase: 'Test SDF Network ; September 2015'
});
```

## 🎯 Available Functions

### Query Functions (Read-only)

```typescript
// Check permission for a wallet
await sdk.check_permission({ wallet: Address });

// Get full risk state
await sdk.get_risk({ wallet: Address });

// Quick freeze check
await sdk.is_frozen({ wallet: Address });

// Get Oracle public key
await sdk.get_oracle_pubkey();
```

### Write Functions

```typescript
// Initialize (one-time)
await sdk.initialize({ oracle_pubkey: BytesN<32> });

// Submit risk (Oracle only)
await sdk.submit_risk({ 
  payload: RiskPayload,
  signature: Signature 
});
```

## 🔗 Integration in Frontend

```typescript
// In your Next.js/React app
import { SentinelSDK } from '@/lib/sentinel-sdk';

// Pre-check before transaction
async function beforeTransaction(userWallet: string) {
  const decision = await sdk.check_permission({ wallet: userWallet });
  
  if (decision.tag === 'Freeze') {
    alert('⛔ This wallet is blocked by Sentinel risk engine');
    return false;
  }
  
  if (decision.tag === 'Limit') {
    maxAmount = Math.min(maxAmount, decision.value);
  }
  
  return true;
}
```

## 📝 Type Definitions

### RiskDecision
```typescript
type RiskDecision = 
  | { tag: 'Allow' }
  | { tag: 'Limit', value: number }
  | { tag: 'Freeze' };
```

### RiskState
```typescript
interface RiskState {
  risk_score: number;  // 0-100
  last_updated: bigint;
  decision: RiskDecision;
}
```

### RiskPayload
```typescript
interface RiskPayload {
  wallet: Address;
  risk_score: number;
  timestamp: bigint;
}
```

## 🚀 Next Steps

1. Build TypeScript bindings: `cd bindings/typescript && npm install && npm run build`
2. Initialize contract with Oracle public key
3. Test SDK functions from frontend
4. Build demo protocol integration
