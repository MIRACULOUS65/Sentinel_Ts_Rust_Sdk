# Service 2: Transaction Graph Engine

## 🕸️ What is this?
A real-time Network Graph engine that monitors Stellar transactions.
It builds a directed graph of `Wallet -> Wallet` payment flows.

## 🚀 Key Features
- **Live Ingestion**: Connects to Stellar Horizon (Testnet/Mainnet).
- **Time Decay**: Old edges fade away; reflects *current* money flow.
- **Analytics**: Calculates PageRank, Centrality, and In/Out Degree.
- **Visual API**: Serves JSON for frontend visualization.
- **Risk Coloring**: Marks nodes Red/Green based on behavior.

## 🛠️ Tech Stack
- **Python (FastAPI)**
- **NetworkX** (Graph Algorithms)
- **Matplotlib** (Static Debug Viz)

## 🏃 Running
```bash
cd service2_graph
pip install -r requirements.txt
python -m uvicorn graph_service:app --port 8009
```
