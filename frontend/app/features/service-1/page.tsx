"use client";

import { Card } from "@/components/ui/card";
import Link from "next/link";
import { ArrowLeft, ExternalLink, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

const API_URL = "https://sentinel-653o.onrender.com";

interface Wallet {
  wallet: string;
  tx_count: number;
  tx_per_hour: number;
  risk_level: "normal" | "medium" | "elevated" | "high";
  explorer_url: string;
  last_updated: string;
}

interface WalletResponse {
  wallets: Wallet[];
  total_wallets: number;
  timestamp: string;
  network: string;
}

interface Operation {
  type: string;
  from_account?: string;
  to?: string;
  amount?: string;
  asset_type?: string;
}

interface Transaction {
  id: string;
  source_account: string;
  created_at: string;
  operations: Operation[];
  explorer_url: string;
  account_url: string;
}

interface TransactionResponse {
  transactions: Transaction[];
  count: number;
  network: string;
}

export default function Service1Page() {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      setIsRefreshing(true);

      // Fetch wallets
      const walletsRes = await fetch(`${API_URL}/explorer/wallets/frequency`);
      if (!walletsRes.ok) throw new Error("Failed to fetch wallets");
      const walletsData: WalletResponse = await walletsRes.json();
      setWallets(walletsData.wallets);
      setLastUpdated(new Date().toLocaleTimeString());

      // Fetch recent transactions
      const txRes = await fetch(`${API_URL}/explorer/transactions/recent?limit=10`);
      if (!txRes.ok) throw new Error("Failed to fetch transactions");
      const txData: TransactionResponse = await txRes.json();
      setTransactions(txData.transactions);

      setError(null);
    } catch (err) {
      setError("Failed to load data from Stellar network");
      console.error(err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (level: string) => {
    const colors = {
      high: "bg-red-50 dark:bg-red-950/20 border-red-500 text-red-900 dark:text-red-300",
      elevated: "bg-yellow-50 dark:bg-yellow-950/20 border-yellow-500 text-yellow-900 dark:text-yellow-300",
      medium: "bg-green-50 dark:bg-green-950/20 border-green-500 text-green-900 dark:text-green-300",
      normal: "bg-blue-50 dark:bg-blue-950/20 border-blue-500 text-blue-900 dark:text-blue-300",
    };
    return colors[level as keyof typeof colors] || colors.normal;
  };

  const getRiskBadgeColor = (level: string) => {
    const colors = {
      high: "bg-red-500 text-white",
      elevated: "bg-yellow-500 text-black",
      medium: "bg-green-500 text-white",
      normal: "bg-blue-500 text-white",
    };
    return colors[level as keyof typeof colors] || colors.normal;
  };

  const getRiskIcon = (level: string) => {
    const icons = {
      high: "🔴",
      elevated: "🟡",
      medium: "🟢",
      normal: "🔵",
    };
    return icons[level as keyof typeof icons] || icons.normal;
  };

  const truncateAddress = (address: string, start = 8, end = 6) => {
    if (address.length <= start + end) return address;
    return `${address.slice(0, start)}...${address.slice(-end)}`;
  };

  const highRiskCount = wallets.filter((w) => w.risk_level === "high").length;
  const elevatedRiskCount = wallets.filter((w) => w.risk_level === "elevated").length;

  return (
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 w-full z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-black/10 dark:border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/features" className="flex items-center space-x-2 group">
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <span className="font-bold">Back to Features</span>
          </Link>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-black dark:bg-white rounded-md"></div>
            <span className="font-bold tracking-tight">SENTINEL</span>
          </div>
        </div>
      </nav>

      <div className="pt-32 pb-20 px-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-block">
            <span className="text-sm font-semibold tracking-wider uppercase border border-black/20 dark:border-white/20 px-4 py-2 rounded-full">
              Service 1: Live Monitoring
            </span>
          </div>
          <h1 className="text-5xl md:text-7xl font-black tracking-tighter">
            Live Stellar Monitor
          </h1>
          <p className="text-xl text-black/60 dark:text-white/60 max-w-2xl mx-auto">
            Real-time wallet tracking and behavioral risk analysis
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <Card className="p-6 border-2 border-black/10 dark:border-white/10 text-center">
            <div className="text-3xl font-black mb-2">{wallets.length}</div>
            <div className="text-sm text-black/60 dark:text-white/60 uppercase tracking-wide">
              Total Wallets
            </div>
          </Card>
          <Card className="p-6 border-2 border-red-500/50 bg-red-50 dark:bg-red-950/20 text-center">
            <div className="text-3xl font-black mb-2 text-red-600 dark:text-red-400">
              {highRiskCount}
            </div>
            <div className="text-sm text-red-600 dark:text-red-400 uppercase tracking-wide">
              High Risk
            </div>
          </Card>
          <Card className="p-6 border-2 border-yellow-500/50 bg-yellow-50 dark:bg-yellow-950/20 text-center">
            <div className="text-3xl font-black mb-2 text-yellow-600 dark:text-yellow-400">
              {elevatedRiskCount}
            </div>
            <div className="text-sm text-yellow-600 dark:text-yellow-400 uppercase tracking-wide">
              Elevated Risk
            </div>
          </Card>
          <Card className="p-6 border-2 border-black/10 dark:border-white/10 text-center">
            <div className="flex items-center justify-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={fetchData}
                disabled={isRefreshing}
                className="hover:bg-black/5 dark:hover:bg-white/5"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
              </Button>
            </div>
            <div className="text-xs text-black/60 dark:text-white/60 uppercase tracking-wide mt-2">
              {lastUpdated ? `Updated ${lastUpdated}` : "Loading..."}
            </div>
          </Card>
        </div>

        {loading && !wallets.length ? (
          <div className="text-center py-20">
            <div className="text-xl text-black/60 dark:text-white/60">
              Loading Stellar network data...
            </div>
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <div className="text-xl text-red-600 dark:text-red-400">{error}</div>
            <Button onClick={fetchData} className="mt-4">
              Retry
            </Button>
          </div>
        ) : (
          <>
            {/* Two-column grid layout */}
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Left Column: Recent Transactions */}
              <div className="space-y-6">
                <h2 className="text-3xl font-black">Recent Transactions</h2>
                <div className="grid gap-4 max-h-[800px] overflow-y-auto pr-2">
                  {transactions.map((tx) => (
                    <Card
                      key={tx.id}
                      className="p-6 border-2 border-black/10 dark:border-white/10 hover:border-black/20 dark:hover:border-white/20 transition-all hover:shadow-lg"
                    >
                      <div className="space-y-3">
                        <div className="flex flex-col gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-black/60 dark:text-white/60 uppercase tracking-wider">
                              TX ID
                            </span>
                            <code className="text-sm font-mono">
                              {truncateAddress(tx.id, 10, 8)}
                            </code>
                          </div>
                          <div className="text-xs text-black/60 dark:text-white/60">
                            {new Date(tx.created_at).toLocaleString()}
                          </div>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-black/60 dark:text-white/60">From:</span>
                          <code className="font-mono">
                            {truncateAddress(tx.source_account, 8, 6)}
                          </code>
                        </div>

                        {tx.operations.length > 0 && (
                          <div className="bg-black/5 dark:bg-white/5 rounded-lg p-3 space-y-2">
                            {tx.operations.map((op, idx) => (
                              <div key={idx} className="text-sm">
                                <span className="font-semibold capitalize">{op.type}</span>
                                {op.type === "payment" && op.to && (
                                  <span className="text-black/60 dark:text-white/60">
                                    {" "}
                                    → {truncateAddress(op.to, 8, 6)} ({op.amount} {op.asset_type === "native" ? "XLM" : op.asset_type})
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="flex gap-2">
                          <a
                            href={tx.explorer_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-black dark:text-white hover:opacity-60 transition-opacity flex items-center gap-1"
                          >
                            View Transaction
                            <ExternalLink className="w-3 h-3" />
                          </a>
                          <span className="text-black/20 dark:text-white/20">•</span>
                          <a
                            href={tx.account_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-black dark:text-white hover:opacity-60 transition-opacity flex items-center gap-1"
                          >
                            View Account
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Right Column: Wallet Activity Monitor */}
              <div className="space-y-6">
                <h2 className="text-3xl font-black">Wallet Activity Monitor</h2>
                <div className="grid gap-4 max-h-[800px] overflow-y-auto pr-2">
                  {wallets.slice(0, 20).map((wallet) => (
                    <Card
                      key={wallet.wallet}
                      className={`p-6 border-2 transition-all hover:shadow-lg ${getRiskColor(
                        wallet.risk_level
                      )}`}
                    >
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{getRiskIcon(wallet.risk_level)}</span>
                          <code className="text-sm font-mono">
                            {truncateAddress(wallet.wallet, 12, 8)}
                          </code>
                        </div>

                        <div className="flex items-center gap-4 text-sm">
                          <span className="font-semibold">
                            {wallet.tx_count} transactions
                          </span>
                          <span className="text-black/60 dark:text-white/60">
                            {wallet.tx_per_hour.toFixed(1)} tx/hour
                          </span>
                        </div>

                        <div className="flex items-center gap-3">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${getRiskBadgeColor(
                              wallet.risk_level
                            )}`}
                          >
                            {wallet.risk_level}
                          </span>
                          <a
                            href={wallet.explorer_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 px-4 py-2 bg-black dark:bg-white text-white dark:text-black rounded-lg hover:opacity-80 transition-opacity text-sm font-medium"
                          >
                            View on Explorer
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
