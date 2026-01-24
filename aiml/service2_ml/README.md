# Service 4: Streaming ML Risk Engine

A production-grade behavioral anomaly detection engine for Stellar transactions.

## Features

- **Pattern-Specific Scoring**: 6 distinct anomaly patterns (circular, bot, burst, fan-out, layering, dust)
- **Diverse Risk Scores**: Full 0-100 range with proper distribution
- **Streaming API**: Real-time ingestion and scoring via REST and WebSocket
- **Explainable Reasons**: Human-readable explanations for each risk score

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# 1. Generate synthetic data
python -m service4_ml generate --wallets 500 --hours 48

# 2. Train the model  
python -m service4_ml train --dataset synthetic_dataset.jsonl

# 3. Run the API server
python -m service4_ml serve --port 8084
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ingest` | POST | Ingest transaction, get risk score |
| `/risk/{wallet}` | GET | Get risk score for wallet |
| `/wallets` | GET | List wallets with risk scores |
| `/stream` | WebSocket | Real-time risk updates |
| `/start-horizon` | POST | Start Stellar Horizon streaming |
| `/stop-horizon` | POST | Stop Horizon streaming |

## Output Contract

```json
{
  "wallet": "GABCD...",
  "risk_score": 87,
  "reason": "abnormal circular transfers"
}
```

## Risk Score Mapping

| Score | Action | Description |
|-------|--------|-------------|
| 0-30 | Allow | Normal behavior |
| 31-69 | Limit | Suspicious, needs monitoring |
| 70-100 | Freeze | High risk anomaly |

## Pattern Detection

| Pattern | Description | Signals |
|---------|-------------|---------|
| Circular | A→B→C→A loops | High return_ratio, self_transfer_ratio |
| Bot | Repetitive payments | Same amount, same recipient |
| Burst | Sudden activity spike | High tx_velocity, tx_count |
| Fan-out | Many recipients | High unique_recipients, fan_out_score |
| Layering | Multi-hop transfers | Low avg_interval, high velocity |
| Dust | Tiny spam | High dust_tx_ratio, low amounts |

## Architecture

```
┌─────────────┐    ┌───────────────┐    ┌─────────────────┐
│ Data Ingest │───▶│ State Manager │───▶│ Feature Extract │
└─────────────┘    └───────────────┘    └────────┬────────┘
                                                  │
┌─────────────┐    ┌───────────────┐    ┌────────▼────────┐
│ Risk Output │◀───│ Pattern Score │◀───│ Anomaly Model  │
└─────────────┘    └───────────────┘    └─────────────────┘
```
