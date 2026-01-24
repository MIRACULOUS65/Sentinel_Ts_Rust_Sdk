# Service 1: Horizon Data Fetcher

Real-time Stellar transaction monitoring and wallet frequency tracking service.

## 🎯 Purpose

Fetches live transaction data from Stellar Horizon API and tracks wallet behavior patterns for anomaly detection.

## 📡 API Endpoints

### Production URL (After Render Deployment)
```
https://your-service-name.onrender.com
```

### Available Endpoints

#### 1. Get Wallet Frequencies with Explorer URLs
```
GET /explorer/wallets/frequency
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

#### 2. Get Recent Transactions
```
GET /explorer/transactions/recent?limit=10
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "883bf459b566148bdd1410c43ac1d035fe72eac501907ea684fc9f54d4dcca97",
      "source_account": "GCTDSRPBBJFE75NGRRYMWISY7RRLGLVEF55CUHZ3P6LK2COD34WEXJE2",
      "created_at": "2026-01-24T07:26:09Z",
      "explorer_url": "https://stellar.expert/explorer/testnet/tx/883bf459...",
      "account_url": "https://stellar.expert/explorer/testnet/account/GCTDSRP..."
    }
  ],
  "count": 10,
  "network": "testnet"
}
```

#### 3. Get Specific Wallet
```
GET /explorer/wallet/{wallet_address}
```

#### 4. Health Check
```
GET /health
```

## 🚀 Deploy to Render

### Automatic Deployment (Using render.yaml)

1. **Code is already on GitHub**: ✅ Done!
   - Repository: `https://github.com/MIRACULOUS65/Sentinel`
   - Service location: `aiml/service1_horizon/`

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Blueprint**
   - Connect your `Sentinel` repository
   - Render will auto-detect `render.yaml`
   - Click **Apply** to deploy

3. **Get Your URL**:
   - After deployment: `https://stellar-horizon-fetcher.onrender.com`
   - Update this URL in your frontend code

### Manual Deployment

1. Go to Render Dashboard
2. New + → Web Service
3. Connect `Sentinel` repository
4. Configure:
   - **Name**: `stellar-horizon-fetcher`
   - **Root Directory**: `aiml/service1_horizon`
   - **Runtime**: Python 3
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn horizon_service:app --host 0.0.0.0 --port $PORT`
5. Deploy!

## 💻 Frontend Integration

### Next.js Example

```typescript
const API_URL = 'https://stellar-horizon-fetcher.onrender.com';

// Fetch wallet frequencies
const response = await fetch(`${API_URL}/explorer/wallets/frequency`);
const data = await response.json();

// Display wallets with risk levels
data.wallets.map(wallet => (
  <div className={`risk-${wallet.risk_level}`}>
    <span>{wallet.wallet}</span>
    <span>{wallet.tx_per_hour} tx/h</span>
    <a href={wallet.explorer_url} target="_blank">
      View on Stellar Expert →
    </a>
  </div>
));
```

### Node.js Example

```javascript
const axios = require('axios');

const API_URL = 'https://stellar-horizon-fetcher.onrender.com';

// Get wallet frequencies
const { data } = await axios.get(`${API_URL}/explorer/wallets/frequency`);

data.wallets.forEach(wallet => {
  console.log(`${wallet.wallet}: ${wallet.tx_per_hour} tx/h (${wallet.risk_level})`);
  console.log(`Explorer: ${wallet.explorer_url}`);
});
```

### Vanilla JavaScript

```javascript
fetch('https://stellar-horizon-fetcher.onrender.com/explorer/wallets/frequency')
  .then(res => res.json())
  .then(data => {
    data.wallets.forEach(wallet => {
      console.log(wallet.wallet, wallet.risk_level);
    });
  });
```

## 🔑 Risk Levels

| Level | TX/Hour | Indicator | Meaning |
|-------|---------|-----------|---------|
| `normal` | < 10 | 🔵 | Normal activity |
| `medium` | 10-20 | 🟢 | Moderate activity |
| `elevated` | 20-50 | 🟡 | High activity |
| `high` | > 50 | 🔴 | Suspicious activity |

## 📁 Files

- `horizon_service.py` - Main FastAPI service
- `requirements.txt` - Python dependencies
- `README.md` - Frontend integration guide
- `quick_test.py` - API test script
- `.env.example` - Environment config template

## ✅ Features

- ✅ Real-time Stellar testnet transaction fetching
- ✅ Wallet frequency tracking (tx/hour)
- ✅ Risk level classification
- ✅ Stellar Expert URLs for all transactions and wallets
- ✅ CORS enabled for frontend integration
- ✅ Caching layer (10s TTL)
- ✅ Health check endpoint for Render
- ✅ Auto-retry logic for API failures

## 🔗 Resources

- **GitHub**: https://github.com/MIRACULOUS65/Sentinel
- **Stellar Horizon API**: https://horizon-testnet.stellar.org
- **Stellar Expert**: https://stellar.expert/explorer/testnet
- **Render**: https://dashboard.render.com

## 📝 Next Steps

1. ✅ Code pushed to GitHub
2. 🔜 Deploy to Render
3. 🔜 Get production URL
4. 🔜 Integrate with frontend
5. 🔜 Build Service 2 (ML Engine)