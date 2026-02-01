# Stellar Horizon Data Fetcher - Frontend Integration Guide

## 🚀 Deployed Service URL
```
https://your-service-name.onrender.com
```
*(Replace with your actual Render URL after deployment)*

---

## 📡 API Endpoints for Frontend

### 1. Get Wallet Frequencies with Explorer URLs (Recommended)
```
GET https://your-service-name.onrender.com/explorer/wallets/frequency
```

**Response:**
```json
{
  "wallets": [
    {
      "wallet": "GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
      "tx_count": 13,
      "tx_per_hour": 13.0,
      "risk_level": "medium",
      "explorer_url": "https://stellar.expert/explorer/testnet/account/GAIH3UL...",
      "last_updated": "2026-01-24T07:30:00"
    }
  ],
  "total_wallets": 27,
  "network": "testnet"
}
```

### 2. Get Recent Transactions with Explorer URLs
```
GET https://your-service-name.onrender.com/explorer/transactions/recent?limit=10
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "883bf459b566148bdd1410c43ac1d035fe72eac501907ea684fc9f54d4dcca97",
      "source_account": "GCTDSRPBBJFE75NGRRYMWISY7RRLGLVEF55CUHZ3P6LK2COD34WEXJE2",
      "created_at": "2026-01-24T07:26:09Z",
      "operations": [...],
      "explorer_url": "https://stellar.expert/explorer/testnet/tx/883bf459...",
      "account_url": "https://stellar.expert/explorer/testnet/account/GCTDSRP..."
    }
  ],
  "count": 10,
  "network": "testnet"
}
```

### 3. Get Specific Wallet Details
```
GET https://your-service-name.onrender.com/explorer/wallet/{wallet_address}
```

**Response:**
```json
{
  "wallet": "GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR",
  "tx_count": 13,
  "tx_per_hour": 13.0,
  "risk_level": "medium",
  "explorer_url": "https://stellar.expert/explorer/testnet/account/GAIH3UL...",
  "network": "testnet"
}
```

---

## 💻 Next.js Integration

### App Router (app/page.tsx)
```typescript
'use client';

import { useEffect, useState } from 'react';

const API_URL = 'https://your-service-name.onrender.com';

interface Wallet {
  wallet: string;
  tx_count: number;
  tx_per_hour: number;
  risk_level: string;
  explorer_url: string;
}

export default function Dashboard() {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch wallet data
    const fetchWallets = async () => {
      try {
        const response = await fetch(`${API_URL}/explorer/wallets/frequency`);
        const data = await response.json();
        setWallets(data.wallets);
      } catch (error) {
        console.error('Error fetching wallets:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWallets();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchWallets, 10000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-500';
      case 'elevated': return 'text-yellow-500';
      case 'medium': return 'text-green-500';
      default: return 'text-blue-500';
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Stellar Wallet Monitor</h1>
      
      <div className="grid gap-4">
        {wallets.map((wallet) => (
          <div key={wallet.wallet} className="border p-4 rounded">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-mono text-sm">{wallet.wallet.slice(0, 20)}...</p>
                <p className={`text-sm ${getRiskColor(wallet.risk_level)}`}>
                  {wallet.tx_per_hour} tx/hour - {wallet.risk_level}
                </p>
              </div>
              
              <a 
                href={wallet.explorer_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                View on Stellar Expert →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🟢 Node.js Integration

### Express.js Backend
```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const API_URL = 'https://your-service-name.onrender.com';

// Get wallet frequencies
app.get('/api/wallets', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/explorer/wallets/frequency`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get recent transactions
app.get('/api/transactions', async (req, res) => {
  try {
    const limit = req.query.limit || 10;
    const response = await axios.get(
      `${API_URL}/explorer/transactions/recent?limit=${limit}`
    );
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Simple Fetch (Vanilla JS)
```javascript
const API_URL = 'https://your-service-name.onrender.com';

// Fetch wallet frequencies
async function getWallets() {
  const response = await fetch(`${API_URL}/explorer/wallets/frequency`);
  const data = await response.json();
  
  data.wallets.forEach(wallet => {
    console.log(`Wallet: ${wallet.wallet}`);
    console.log(`Risk: ${wallet.risk_level}`);
    console.log(`Explorer: ${wallet.explorer_url}`);
  });
}

// Fetch recent transactions
async function getTransactions(limit = 10) {
  const response = await fetch(
    `${API_URL}/explorer/transactions/recent?limit=${limit}`
  );
  const data = await response.json();
  
  data.transactions.forEach(tx => {
    console.log(`TX: ${tx.id}`);
    console.log(`Explorer: ${tx.explorer_url}`);
  });
}

// Call functions
getWallets();
getTransactions(5);
```

---

## 🎨 React Component Example

```tsx
import React, { useEffect, useState } from 'react';

const API_URL = 'https://your-service-name.onrender.com';

export function WalletList() {
  const [wallets, setWallets] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/explorer/wallets/frequency`)
      .then(res => res.json())
      .then(data => setWallets(data.wallets));
  }, []);

  return (
    <div>
      {wallets.map(wallet => (
        <div key={wallet.wallet}>
          <span>{wallet.wallet.slice(0, 20)}...</span>
          <span className={`risk-${wallet.risk_level}`}>
            {wallet.tx_per_hour} tx/h
          </span>
          <a href={wallet.explorer_url} target="_blank">
            View →
          </a>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔑 Risk Levels

| Level | TX/Hour | Color | Meaning |
|-------|---------|-------|---------|
| `normal` | < 10 | 🔵 Blue | Normal activity |
| `medium` | 10-20 | 🟢 Green | Moderate activity |
| `elevated` | 20-50 | 🟡 Yellow | High activity |
| `high` | > 50 | 🔴 Red | Suspicious activity |

---

## 📦 Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to `me_only/service1_horizon` folder
4. Configure:
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn horizon_service:app --host 0.0.0.0 --port $PORT`
5. Deploy and copy your URL
6. Replace `https://your-service-name.onrender.com` in your frontend code

---

## ✅ Ready to Use!

All endpoints return data with:
- ✅ Stellar Expert URLs (clickable links)
- ✅ Risk levels (for color coding)
- ✅ Network type (testnet/mainnet)
- ✅ CORS enabled (works from any frontend)
