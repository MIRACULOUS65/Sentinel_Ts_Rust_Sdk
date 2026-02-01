"""
Service 2: Live Transaction Network Graph
Real-time, time-decayed graph with behavioral analytics
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse, StreamingResponse
import networkx as nx
import httpx
import asyncio
import random
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import math
import os
import io
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

# Config
SERVICE1_URL = os.getenv("SERVICE1_URL", "https://sentinel-653o.onrender.com")
HORIZON_URL = os.getenv("HORIZON_API_URL", "https://horizon-testnet.stellar.org")
UPDATE_INTERVAL = 5  # seconds
TIME_WINDOW = 3600  # 1 hour sliding window
DECAY_RATE = 0.1  # exponential decay rate

app = FastAPI(title="Stellar Live Graph API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
live_graph = nx.DiGraph()
edge_timestamps = defaultdict(list)  # (from, to) -> [timestamps]
edge_amounts = defaultdict(list)  # (from, to) -> [amounts]
last_update = None


class LiveGraphBuilder:
    """Build time-decayed transaction graph"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.edge_timestamps = defaultdict(list)
        self.edge_amounts = defaultdict(list)
    
    def add_transaction(self, from_w: str, to_w: str, amount: float, timestamp: str):
        """Add transaction with timestamp"""
        self.graph.add_node(from_w)
        self.graph.add_node(to_w)
        
        edge_key = (from_w, to_w)
        self.edge_timestamps[edge_key].append(timestamp)
        self.edge_amounts[edge_key].append(amount)
        
        # Calculate time-decayed weight
        weight = self.calculate_edge_weight(edge_key)
        
        if self.graph.has_edge(from_w, to_w):
            self.graph[from_w][to_w]["weight"] = weight
            self.graph[from_w][to_w]["raw_count"] = len(self.edge_timestamps[edge_key])
            self.graph[from_w][to_w]["total_amount"] = sum(self.edge_amounts[edge_key])
        else:
            self.graph.add_edge(from_w, to_w, 
                              weight=weight,
                              raw_count=1,
                              total_amount=amount)
    
    def calculate_edge_weight(self, edge_key) -> float:
        """Calculate time-decayed weight for edge"""
        timestamps = self.edge_timestamps[edge_key]
        amounts = self.edge_amounts[edge_key]
        
        now = datetime.now(timezone.utc)
        total_weight = 0.0
        
        for ts, amt in zip(timestamps, amounts):
            try:
                # Ensure ts string is parsed as timezone-aware
                if 'Z' in ts:
                     tx_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    # Assume UTC if naive string came from somewhere else, but Horizon gives Z
                    tx_time = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
                    
                age_hours = (now - tx_time).total_seconds() / 3600
                
                # Exponential decay: weight = amount * e^(-decay_rate * age)
                decay_factor = math.exp(-DECAY_RATE * age_hours)
                total_weight += amt * decay_factor
            except Exception as e:
                # print(f"Error calcing weight: {e}")
                total_weight += amt * 0.5  # fallback
        
        return total_weight
    
    def prune_old_transactions(self):
        """Remove transactions outside time window"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=TIME_WINDOW)
        
        for edge_key in list(self.edge_timestamps.keys()):
            timestamps = self.edge_timestamps[edge_key]
            amounts = self.edge_amounts[edge_key]
            
            # Filter out old transactions
            filtered = [(ts, amt) for ts, amt in zip(timestamps, amounts)
                       if datetime.fromisoformat(ts.replace('Z', '+00:00')) > cutoff]
            
            if filtered:
                self.edge_timestamps[edge_key] = [t[0] for t in filtered]
                self.edge_amounts[edge_key] = [t[1] for t in filtered]
            else:
                # Remove edge if all transactions expired
                from_w, to_w = edge_key
                if self.graph.has_edge(from_w, to_w):
                    self.graph.remove_edge(from_w, to_w)
                del self.edge_timestamps[edge_key]
                del self.edge_amounts[edge_key]


class BehavioralAnalytics:
    """Compute behavioral metrics for nodes"""
    
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        
        # Pre-compute expensive metrics
        self.pagerank = nx.pagerank(graph, weight='weight') if len(graph.nodes()) > 0 else {}
        self.clustering = {}
        for node in graph.nodes():
            try:
                self.clustering[node] = nx.clustering(graph.to_undirected(), node)
            except:
                self.clustering[node] = 0.0
    
    def analyze_node(self, node: str) -> Dict:
        """Get all behavioral metrics for a node"""
        if node not in self.graph:
            return self.empty_metrics(node)
        
        in_deg = self.graph.in_degree(node, weight='weight')
        out_deg = self.graph.out_degree(node, weight='weight')
        
        # In/out ratio
        ratio = in_deg / out_deg if out_deg > 0 else float('inf')
        
        # Unique counterparties
        in_neighbors = list(self.graph.predecessors(node))
        out_neighbors = list(self.graph.successors(node))
        unique_counterparties = len(set(in_neighbors + out_neighbors))
        
        # Edge weight entropy
        entropy = self.calculate_entropy(node)
        
        # Cycle participation
        in_cycle = self.is_in_cycle(node)
        
        return {
            "wallet": node,
            "in_degree": round(in_deg, 2),
            "out_degree": round(out_deg, 2),
            "in_out_ratio": round(ratio, 2) if ratio != float('inf') else None,
            "clustering_coefficient": round(self.clustering.get(node, 0.0), 4),
            "pagerank": round(self.pagerank.get(node, 0.0), 6),
            "unique_counterparties": unique_counterparties,
            "edge_weight_entropy": round(entropy, 4),
            "in_cycle": in_cycle,
            "risk_score": self.calculate_risk_score(in_deg, out_deg, ratio, entropy, in_cycle)
        }
    
    def calculate_entropy(self, node: str) -> float:
        """Calculate edge weight entropy for node"""
        if node not in self.graph:
            return 0.0
        
        # Get all edge weights
        weights = []
        for _, _, data in self.graph.out_edges(node, data=True):
            weights.append(data.get('weight', 0))
        
        if not weights:
            return 0.0
        
        total = sum(weights)
        if total == 0:
            return 0.0
        
        # Shannon entropy
        entropy = 0.0
        for w in weights:
            p = w / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy
    
    def is_in_cycle(self, node: str) -> bool:
        """Check if node participates in any cycle"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                if node in cycle and len(cycle) <= 5:
                    return True
        except:
            pass
        return False
    
    def calculate_risk_score(self, in_deg, out_deg, ratio, entropy, in_cycle) -> float:
        """Calculate composite risk score (0-100)"""
        score = 0.0
        
        # High in-degree (money mule)
        if in_deg > 10:
            score += min(in_deg * 2, 25)
        
        # High out-degree (distributor)
        if out_deg > 10:
            score += min(out_deg * 2, 25)
        
        # Imbalanced ratio
        if ratio and (ratio > 5 or ratio < 0.2):
            score += 15
        
        # Low entropy (focused activity)
        if entropy < 1.0:
            score += 15
        
        # Cycle participation
        if in_cycle:
            score += 20
        
        return min(score, 100.0)
    
    def empty_metrics(self, node: str) -> Dict:
        return {
            "wallet": node,
            "in_degree": 0,
            "out_degree": 0,
            "in_out_ratio": None,
            "clustering_coefficient": 0.0,
            "pagerank": 0.0,
            "unique_counterparties": 0,
            "edge_weight_entropy": 0.0,
            "in_cycle": False,
            "risk_score": 0.0
        }


async def fetch_recent_transactions():
    """Fetch latest transactions directly from Horizon API"""
    transactions = []
    
    # Primary Source: Horizon API /payments
    try:
        print("Fetching live payments from Horizon API...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch most recent payments directly
            response = await client.get(f"{HORIZON_API}/payments?limit=50&order=desc")
            if response.status_code != 200:
                print(f"⚠️ Horizon API Error: {response.text}")
                return []
                
            data = response.json()
            
            # Normalize Horizon data
            for record in data.get("_embedded", {}).get("records", []):
                # Only interested in direct payments
                if record["type"] == "payment":
                    transactions.append({
                        "from": record.get("from"),
                        "to": record.get("to"),
                        "amount": float(record.get("amount", 0)),
                        "timestamp": record.get("created_at"),
                        "type": "payment"
                    })
                elif record["type"] == "create_account":
                     transactions.append({
                        "from": record.get("source_account"), # Funder
                        "to": record.get("account"),          # New account
                        "amount": float(record.get("starting_balance", 0)),
                        "timestamp": record.get("created_at"),
                        "type": "create_account"
                    })
            
            print(f"✅ Fetched {len(transactions)} payments from Stellar")
            return transactions
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return []


async def update_live_graph():
    """Update live graph with new transactions"""
    global live_graph, edge_timestamps, edge_amounts, last_update
    
    print(f"[{datetime.now(timezone.utc).isoformat()}] Updating live graph...")
    
    # Fetch unified transaction list
    payments = await fetch_recent_transactions()
    
    if not payments:
        print("  No new payments found.")
        return

    builder = LiveGraphBuilder()
    builder.edge_timestamps = edge_timestamps
    builder.edge_amounts = edge_amounts
    builder.graph = live_graph
    
    count = 0
    # Add new transactions
    for pay in payments:
        from_w = pay.get("from")
        to_w = pay.get("to")
        amount = pay.get("amount", 0.0)
        timestamp = pay.get("timestamp")
        
        if from_w and to_w:
            builder.add_transaction(from_w, to_w, amount, timestamp)
            count += 1
    
    # Prune old transactions
    builder.prune_old_transactions()
    
    # Update global state
    live_graph = builder.graph
    edge_timestamps = builder.edge_timestamps
    edge_amounts = builder.edge_amounts
    last_update = datetime.utcnow().isoformat()
    
    print(f"  Processed {count} payments. Graph: {len(live_graph.nodes())} nodes, {len(live_graph.edges())} edges")



@app.get("/")
async def root():
    return {
        "service": "Stellar Live Graph API",
        "version": "2.0.0",
        "endpoints": {
            "live_graph": "/graph/live",
            "wallet_subgraph": "/graph/wallet/{id}",
            "multi_wallet_subgraph": "/graph/subgraph?wallets=A,B,C"
        },
        "config": {
            "update_interval": f"{UPDATE_INTERVAL}s",
            "time_window": f"{TIME_WINDOW}s",
            "decay_rate": DECAY_RATE
        }
    }


@app.get("/graph/visualize", responses={200: {"content": {"image/png": {}}}})
async def visualize_graph(limit: int = 100):
    """
    Generate a real-time static image of the transaction graph.
    Nodes are color-coded by AI RISK SCORE:
    RED: High Risk (>75) - Probable Fraud
    ORANGE: Medium Risk (>50) - Suspicious
    GREEN: Low Risk (<50) - Normal
    """
    global live_graph
    
    # 1. Get Top N nodes by Degree
    if len(live_graph) > limit:
        degrees = dict(live_graph.degree(weight='weight'))
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:limit]
        subgraph = live_graph.subgraph(top_nodes)
    else:
        subgraph = live_graph
        
    if len(subgraph.nodes()) == 0:
        return JSONResponse(status_code=404, content={"message": "No data in graph yet."})

    # 2. Analyze Probabilities (Risk Scoring)
    analytics = BehavioralAnalytics(subgraph)
    node_colors = []
    node_sizes = []
    
    for node in subgraph.nodes():
        metrics = analytics.analyze_node(node)
        score = metrics["risk_score"]
        
        # Color by Risk Score
        if score >= 75:
            node_colors.append('#EF4444') # Red (High Risk)
        elif score >= 50:
            node_colors.append('#F59E0B') # Orange (Medium Risk)
        else:
            node_colors.append('#10B981') # Green (Safe)
            
        # Size by PageRank (Influence)
        pagerank = metrics["pagerank"]
        node_sizes.append(300 + (pagerank * 5000))

    # 3. Draw Graph
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(subgraph, k=0.15, iterations=20)
    
    nx.draw_networkx_nodes(subgraph, pos, node_size=node_sizes, node_color=node_colors, alpha=0.9)
    nx.draw_networkx_edges(subgraph, pos, alpha=0.3, edge_color='#9CA3AF', arrows=True)
    
    # Label high-risk nodes explicitly
    labels = {}
    for node in subgraph.nodes():
        metrics = analytics.analyze_node(node)
        if metrics["risk_score"] > 50:
            labels[node] = f"{node[:4]} (Risk:{int(metrics['risk_score'])})"
            
    nx.draw_networkx_labels(subgraph, pos, labels, font_size=8, font_weight='bold')
    
    plt.title(f"Live Fraud Detection Network\nNodes: {len(subgraph.nodes())} | High Risk: {len([c for c in node_colors if c == '#EF4444'])}")
    plt.axis('off')
    
    # 4. Save
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    
    return StreamingResponse(buf, media_type="image/png")


class TransactionInjection(BaseModel):
    from_w: str
    to_w: str
    amount: float

@app.post("/debug/inject")
async def inject_transaction(tx: TransactionInjection):
    """Inject a simulated transaction for testing fraud patterns"""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    builder = LiveGraphBuilder()
    builder.edge_timestamps = edge_timestamps
    builder.edge_amounts = edge_amounts
    builder.graph = live_graph
    
    builder.add_transaction(tx.from_w, tx.to_w, tx.amount, timestamp)
    
    return {"status": "injected", "tx": tx.dict()}



@app.get("/graph/live")
async def get_live_graph(limit: int = Query(default=100, ge=1, le=500), sort_by: str = "degree"):
    """
    Get global live network graph
    sort_by: "degree" (influencers) or "latest" (recent activity)
    """
    
    if len(live_graph.nodes()) == 0:
        return {
            "nodes": [],
            "edges": [],
            "stats": {"nodes": 0, "edges": 0},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    top_nodes = []
    
    if sort_by == "latest":
        # Sort by most recent interaction
        node_timestamps = {}
        for (u, v), timestamps in edge_timestamps.items():
            if not timestamps: continue
            # Parse last timestamp
            last_ts = timestamps[-1]
            node_timestamps[u] = max(node_timestamps.get(u, ""), last_ts)
            node_timestamps[v] = max(node_timestamps.get(v, ""), last_ts)
            
        top_nodes = sorted(
            node_timestamps.keys(),
            key=lambda n: node_timestamps[n],
            reverse=True
        )[:limit]
    elif sort_by == "random":
        # Random Sampling (User Request: "monitor randomly every time")
        all_nodes = list(live_graph.nodes())
        if len(all_nodes) > limit:
            top_nodes = random.sample(all_nodes, limit)
        else:
            top_nodes = all_nodes
    else:
        # Default: Sort by degree (Importance)
        top_nodes = sorted(
            live_graph.nodes(),
            key=lambda n: live_graph.degree(n, weight='weight'),
            reverse=True
        )[:limit]
    
    subgraph = live_graph.subgraph(top_nodes)
    analytics = BehavioralAnalytics(subgraph)
    
    nodes = []
    for node in subgraph.nodes():
        metrics = analytics.analyze_node(node)
        nodes.append({
            "id": node,
            "label": node[:10] + "...",
            **metrics
        })
    
    edges = []
    for source, target in subgraph.edges():
        edge_data = subgraph[source][target]
        edges.append({
            "source": source,
            "target": target,
            "weight": round(edge_data.get('weight', 0), 2),
            "raw_count": edge_data.get('raw_count', 0),
            "total_amount": round(edge_data.get('total_amount', 0), 2)
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "total_nodes": len(live_graph.nodes()),
            "total_edges": len(live_graph.edges())
        },
        "timestamp": last_update
    }


@app.get("/graph/wallet/{wallet_id}")
async def get_wallet_subgraph(wallet_id: str, depth: int = Query(default=1, ge=1, le=3)):
    """
    Get subgraph for specific wallet (ego network)
    depth=1: wallet + direct neighbors
    depth=2: wallet + neighbors + neighbors of neighbors
    """
    
    if wallet_id not in live_graph:
        raise HTTPException(404, f"Wallet {wallet_id} not found in live graph")
    
    # Build ego network
    ego_nodes = {wallet_id}
    current_layer = {wallet_id}
    
    for _ in range(depth):
        next_layer = set()
        for node in current_layer:
            next_layer.update(live_graph.predecessors(node))
            next_layer.update(live_graph.successors(node))
        ego_nodes.update(next_layer)
        current_layer = next_layer
    
    subgraph = live_graph.subgraph(ego_nodes)
    analytics = BehavioralAnalytics(subgraph)
    
    # Build response
    nodes = []
    for node in subgraph.nodes():
        metrics = analytics.analyze_node(node)
        nodes.append({
            "id": node,
            "label": node[:10] + "...",
            "is_center": node == wallet_id,
            **metrics
        })
    
    edges = []
    for source, target in subgraph.edges():
        edge_data = subgraph[source][target]
        edges.append({
            "source": source,
            "target": target,
            "weight": round(edge_data.get('weight', 0), 2),
            "raw_count": edge_data.get('raw_count', 0),
            "total_amount": round(edge_data.get('total_amount', 0), 2)
        })
    
    return {
        "wallet": wallet_id,
        "depth": depth,
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges)
        },
        "timestamp": last_update
    }


@app.get("/graph/subgraph")
async def get_multi_wallet_subgraph(wallets: str = Query(...)):
    """
    Get combined subgraph for multiple wallets
    Shows interactions between specified wallets + their neighbors
    """
    
    wallet_list = [w.strip() for w in wallets.split(',') if w.strip()]
    
    if not wallet_list:
        raise HTTPException(400, "No wallets provided")
    
    # Build combined ego network
    ego_nodes = set(wallet_list)
    for wallet in wallet_list:
        if wallet in live_graph:
            ego_nodes.update(live_graph.predecessors(wallet))
            ego_nodes.update(live_graph.successors(wallet))
    
    subgraph = live_graph.subgraph(ego_nodes)
    analytics = BehavioralAnalytics(subgraph)
    
    # Build response
    nodes = []
    for node in subgraph.nodes():
        metrics = analytics.analyze_node(node)
        nodes.append({
            "id": node,
            "label": node[:10] + "...",
            "monitored": node in wallet_list,
            **metrics
        })
    
    edges = []
    for source, target in subgraph.edges():
        edge_data = subgraph[source][target]
        edges.append({
            "source": source,
            "target": target,
            "weight": round(edge_data.get('weight', 0), 2),
            "raw_count": edge_data.get('raw_count', 0),
            "total_amount": round(edge_data.get('total_amount', 0), 2)
        })
    
    # Analyze interactions between monitored wallets
    interactions = {}
    for i, w1 in enumerate(wallet_list):
        for w2 in wallet_list[i+1:]:
            if subgraph.has_edge(w1, w2) or subgraph.has_edge(w2, w1):
                w1_to_w2 = subgraph[w1][w2]['weight'] if subgraph.has_edge(w1, w2) else 0
                w2_to_w1 = subgraph[w2][w1]['weight'] if subgraph.has_edge(w2, w1) else 0
                
                interactions[f"{w1[:8]}↔{w2[:8]}"] = {
                    "wallet1": w1,
                    "wallet2": w2,
                    "w1_to_w2": round(w1_to_w2, 2),
                    "w2_to_w1": round(w2_to_w1, 2),
                    "total": round(w1_to_w2 + w2_to_w1, 2)
                }
    
    return {
        "wallets": wallet_list,
        "nodes": nodes,
        "edges": edges,
        "interactions": interactions,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "monitored_wallets": len(wallet_list)
        },
        "timestamp": last_update
    }


# Store recent ledger operations for the "Details" view
recent_ledger_ops = deque(maxlen=50)

@app.get("/ledger/recent")
async def get_ledger_recent():
    """Get list of recent ledger operations with semantic details."""
    return list(recent_ledger_ops)

def prune_old_transactions():
    """Remove edges older than TIME_WINDOW"""
    global live_graph
    # Simple pruning to avoid memory explosion
    # For now, just clear really old keys if needed or rely on sliding window logic
    pass 
    # Proper logic: iterate all edges, check timestamps. 
    # Since we are fetching repeatedly, let's keep it simple to avoid blocking loop.


@app.get("/stats/history")
async def get_stats_history(seconds: int = 60):
    """
    Get aggregated transaction volume per second for the last N seconds.
    Used for the Time-Series Chart (Ledger Performance).
    """
    if not edge_timestamps:
        return {"labels": [], "volume": []}
        
    now = datetime.now(timezone.utc)
    buckets = defaultdict(int)
    
    # Iterate all filtered timestamps
    # Note: efficient enough for 100-500 nodes.
    cutoff = now - timedelta(seconds=seconds)
    
    for timestamps in edge_timestamps.values():
        for ts_str in timestamps:
            try:
                if 'Z' in ts_str:
                    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
                
                if dt > cutoff:
                    # Bucket by HH:MM:SS
                    time_key = dt.strftime("%H:%M:%S")
                    buckets[time_key] += 1
            except:
                pass
                
    # Fill gaps
    labels = []
    volume = []
    for i in range(seconds):
        t = cutoff + timedelta(seconds=i)
        key = t.strftime("%H:%M:%S")
        labels.append(key)
        volume.append(buckets.get(key, 0))
        
    return {
        "labels": labels,
        "volume": volume,
        "total_tx_in_window": sum(volume)
    }


# Background task
@app.on_event("startup")
async def startup_event():
    """Start live graph updates"""
    asyncio.create_task(update_graph_task())


async def update_graph_task():
    """Continuously update graph"""
    global live_graph
    async with httpx.AsyncClient() as client:
        while True:
            try:
                print(f"[{datetime.utcnow().isoformat()}] Updating live graph...")
                
                # Fetch OPERATIONS (Create Account, Payment, Contract Calls) instead of just Payments
                url = f"{HORIZON_URL}/operations?order=desc&limit=50&include_failed=true"
                print("Fetching live operations from Horizon API...")
                
                response = await client.get(url)
                if response.status_code != 200:
                    print(f"Error fetching data: {response.status_code}")
                    await asyncio.sleep(2)
                    continue
                    
                data = response.json()
                records = data.get("_embedded", {}).get("records", [])
                
                if not records:
                    print("No records found.")
                    continue
                
                print(f"✅ Fetched {len(records)} operations from Stellar")

                new_nodes = set()
                new_edges = 0
                
                for record in records:
                    op_type = record.get("type")
                    tx_hash = record.get("transaction_hash")
                    created_at = record.get("created_at")
                    
                    # Parse based on type
                    # Horizon operations endpoint uses 'source_account', 'funder', 'account', 'to', 'from'
                    source = record.get("source_account") or record.get("funder") or record.get("from")
                    target = record.get("to") or record.get("account") or record.get("into")
                    
                    # Debug if we miss source
                    if not source:
                        print(f"DEBUG: Record keys for type {op_type}: {list(record.keys())}")
                    
                    # Contract / Host Function logic
                    details = f"Type: {op_type}"
                    if op_type == "payment":
                        amount = record.get("amount", "0")
                        asset = record.get("asset_type", "native")
                        details = f"Payment {amount} {asset}"
                        if not target: target = record.get("to")
                    elif op_type == "create_account":
                        start_bal = record.get("starting_balance", "0")
                        details = f"Created Account ({start_bal} XLM)"
                        if not target: target = record.get("account")
                    elif op_type == "invoke_host_function":
                        func = record.get("function", "contract_call")
                        details = f"Contract Call: {func}"
                    elif op_type == "path_payment_strict_send":
                        dest_amt = record.get("dest_amount", "0")
                        details = f"Path Payment -> {dest_amt}"
                    
                    # Add to Live Ledger Log
                    op_log = {
                        "time": datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%H:%M:%S"),
                        "hash": tx_hash[:8] + "...",
                        "type": op_type.upper().replace("_", " "),
                        "source": source[:6] + "..." if source else "Unknown",
                        "details": details
                    }
                    
                    # Dedup log check (simple)
                    if not any(x['hash'] == op_log['hash'] and x['details'] == op_log['details'] for x in recent_ledger_ops):
                        recent_ledger_ops.appendleft(op_log)
                    
                    # Update GRAPH
                    # Always add source if present
                    if source:
                        live_graph.add_node(source, label=source[:4]+"...", type="wallet")
                        new_nodes.add(source)
                        
                    # Always add target if present
                    if target:
                        live_graph.add_node(target, label=target[:4]+"...", type="wallet")
                        new_nodes.add(target)
                    
                    # Update Edge if both exist
                    if source and target and source != target:
                        weight = 1.0
                        if live_graph.has_edge(source, target):
                            # Reinforce existing edge
                            live_graph[source][target]['weight'] += 1.0
                            live_graph[source][target]['last_seen'] = datetime.utcnow()
                        else:
                            live_graph.add_edge(source, target, weight=weight, last_seen=datetime.utcnow())
                            new_edges += 1
                        
                        # Timestamp tracking
                        if (source, target) not in edge_timestamps:
                            edge_timestamps[(source, target)] = deque(maxlen=20)
                        edge_timestamps[(source, target)].append(created_at)

                # Prune old
                prune_old_transactions()
                
                print(f"  Processed {len(records)} ops. Graph: {len(live_graph.nodes())} nodes, {len(live_graph.edges())} edges")
                
                await asyncio.sleep(2) # 2s polling
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                await asyncio.sleep(5)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
