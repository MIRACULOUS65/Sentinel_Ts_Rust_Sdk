# Stellar AI Risk Engine - Service 1: Horizon Data Fetcher

This service fetches real-time Stellar transaction data and tracks wallet frequencies.

## 🚀 Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**:
   ```bash
   cd c:\ml\aiml
   git add .
   git commit -m "Add Service 1: Horizon Data Fetcher"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Blueprint**
   - Connect your GitHub repository (`aiml`)
   - Render will automatically detect `render.yaml`
   - Click **Apply** to deploy

3. **Get Your URL**:
   - After deployment, you'll get: `https://stellar-horizon-fetcher.onrender.com`
   - Copy this URL for frontend integration

### Method 2: Manual Deployment

1. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository

2. **Configure**:
   - **Name**: `stellar-horizon-fetcher`
   - **Root Directory**: `me_only/service1_horizon`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn horizon_service:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables** (Optional):
   - `HORIZON_API_URL` = `https://horizon-testnet.stellar.org`

4. **Deploy**:
   - Click **Create Web Service**
   - Wait for deployment (~5 minutes)

## 📡 Your Deployed Endpoints

Once deployed, replace `YOUR_RENDER_URL` with your actual URL:

```
https://YOUR_RENDER_URL.onrender.com/explorer/wallets/frequency
https://YOUR_RENDER_URL.onrender.com/explorer/transactions/recent
https://YOUR_RENDER_URL.onrender.com/health
```

## ✅ Verify Deployment

Test your deployed service:

```bash
curl https://YOUR_RENDER_URL.onrender.com/health
curl https://YOUR_RENDER_URL.onrender.com/explorer/wallets/frequency
```

## 📝 Frontend Integration

See [README.md](me_only/service1_horizon/README.md) for complete Next.js/Node.js integration examples.

Quick example:
```javascript
const API_URL = 'https://YOUR_RENDER_URL.onrender.com';

const response = await fetch(`${API_URL}/explorer/wallets/frequency`);
const data = await response.json();

// Each wallet has:
// - wallet.explorer_url (Stellar Expert link)
// - wallet.risk_level ("normal", "medium", "elevated", "high")
// - wallet.tx_per_hour (frequency metric)
```

## 🔧 Update Deployment

To update your service:

```bash
cd c:\ml\aiml
git add .
git commit -m "Update Service 1"
git push origin main
```

Render will automatically redeploy.

## 📊 Monitor Your Service

- **Logs**: Render Dashboard → Your Service → Logs
- **Metrics**: Render Dashboard → Your Service → Metrics
- **Health**: `https://YOUR_RENDER_URL.onrender.com/health`

## 🎯 Service Details

- **Folder**: `aiml/me_only/service1_horizon/`
- **Main File**: `horizon_service.py`
- **Port**: Auto-assigned by Render (`$PORT`)
- **Health Check**: `/health` endpoint
- **Auto-deploy**: On git push to main branch
