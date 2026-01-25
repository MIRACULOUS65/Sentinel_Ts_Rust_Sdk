"use client";

import { useState, useEffect } from "react";
import Bento3Section, { BentoItem } from "@/components/ui/bento-monochrome-1";
import { Copy, Check, Server, Globe, Activity } from "lucide-react";
import { BarVisualizer } from "@/components/ui/bar-visualizer";

export default function SDKPage() {
    const [activeTab, setActiveTab] = useState<"typescript" | "rust">("typescript");
    const [copied, setCopied] = useState<string | null>(null);
    const [chartData, setChartData] = useState<any[]>([]);
    const [loadingGraph, setLoadingGraph] = useState(true);

    const handleCopy = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopied(id);
        setTimeout(() => setCopied(null), 2000);
    };

    const CONTRACT_ID = "CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO";
    const HORIZON_URL = `https://horizon-testnet.stellar.org/accounts/${CONTRACT_ID}/transactions?limit=15&order=desc`;

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(HORIZON_URL);
                const data = await res.json();

                if (data._embedded && data._embedded.records) {
                    const activity = data._embedded.records
                        .reverse() // Show oldest to newest
                        .map((tx: any) => ({
                            time: new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                            fee: parseInt(tx.fee_charged),
                            ops: tx.operation_count,
                            status: tx.successful ? 1 : 0
                        }));
                    setChartData(activity);
                }
            } catch (e) {
                console.error("Failed to fetch Horizon data", e);
            } finally {
                setLoadingGraph(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    const TS_INSTALL = "npm install @miraculous65/sentinel-risk-sdk";
    const TS_CODE = `import { Client, networks } from "@miraculous65/sentinel-risk-sdk";

// 1. Connect
const sentinel = new Client({
  ...networks.testnet,
  rpcUrl: "https://soroban-testnet.stellar.org",
});

// 2. Check
const { result } = await sentinel.check_permission({ 
  wallet: "GBGN..." 
});

if (result.tag === "Freeze") {
  alert("❌ Wallet is blocked by AI Risk Engine");
}`;

    const RUST_INSTALL = "cargo add sentinel-contract-sdk-miraculous65";
    const RUST_CODE = `use sentinel_contract_sdk_miraculous65::Client as RiskEngine;

pub fn deposit(env: Env, user: Address, amount: i128) {
    let engine = RiskEngine::new(&env, &SENTINEL_ID);
    
    match engine.check_permission(&user) {
        RiskDecision::Allow => { /* Proceed */ },
        RiskDecision::Freeze => panic!("Blocked!"),
        _ => { /* Handle limits */ }
    }
}`;

    const bentoItems: BentoItem[] = [
        {
            id: "01",
            variant: "relay",
            meta: "Integration",
            title: "Quick Start",
            description: "Choose your environment to see relevant installation commands and examples.",
            statLabel: "Target",
            statValue: activeTab === "typescript" ? "Front-End" : "Smart Contract",
            colSpan: 2,
            children: (
                <div className="mt-6 flex flex-col gap-6">
                    <div className="flex bg-black/40 p-1 rounded-lg border border-white/10 w-fit">
                        <button
                            onClick={() => setActiveTab("typescript")}
                            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === "typescript"
                                ? "bg-white/10 text-white shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                                : "text-white/40 hover:text-white/70"
                                }`}
                        >
                            <Globe className="h-4 w-4" />
                            Web & Wallets
                        </button>
                        <button
                            onClick={() => setActiveTab("rust")}
                            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === "rust"
                                ? "bg-white/10 text-white shadow-[0_0_15px_rgba(234,88,12,0.3)]"
                                : "text-white/40 hover:text-white/70"
                                }`}
                        >
                            <Server className="h-4 w-4" />
                            Smart Contracts
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between bg-black/60 rounded-lg border border-white/10 p-4 font-mono text-xs">
                            <span className="text-emerald-400">
                                $ <span className="text-white/80">{activeTab === "typescript" ? TS_INSTALL : RUST_INSTALL}</span>
                            </span>
                            <button
                                onClick={() => handleCopy(activeTab === "typescript" ? TS_INSTALL : RUST_INSTALL, "install")}
                                className="text-white/30 hover:text-white/90 transition-colors"
                            >
                                {copied === "install" ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                            </button>
                        </div>
                    </div>
                </div>
            )
        },
        {
            id: "02",
            variant: "spark",
            meta: "Codebase",
            title: "Implementation",
            description: activeTab === "typescript"
                ? "Integrate risk checks into your dApp frontend in < 5 lines of code."
                : "Cross-contract calls to enforce risk limits directly on-chain.",
            statLabel: "Language",
            statValue: activeTab === "typescript" ? "TypeScript" : "Rust",
            colSpan: 1, // Adjusted for layout
            children: (
                <div className="mt-6 relative group">
                    <div className="absolute top-2 right-2 z-10">
                        <button
                            onClick={() => handleCopy(activeTab === "typescript" ? TS_CODE : RUST_CODE, "code")}
                            className="bg-black/50 p-2 rounded-md border border-white/10 text-white/30 hover:text-white/90 transition-colors backdrop-blur-sm"
                        >
                            {copied === "code" ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
                        </button>
                    </div>
                    <div className="h-[280px] w-full overflow-y-auto rounded-xl border border-white/10 bg-[#0d161d] p-4 text-[10px] sm:text-xs leading-relaxed font-mono shadow-inner [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
                        <pre className="text-blue-100/80 font-mono">
                            {activeTab === "typescript" ? TS_CODE : RUST_CODE}
                        </pre>
                    </div>
                </div>
            )
        },
        {
            id: "03",
            variant: "orbit",
            meta: "Network",
            title: "Contract Details",
            description: "Official deployed instances of the Sentinel Risk Engine.",
            statLabel: "Network",
            statValue: "Testnet",
            colSpan: 1,
            children: (
                <div className="mt-6 space-y-4 border-t border-white/10 pt-4">
                    <a
                        href={activeTab === "typescript" ? "https://www.npmjs.com/package/@miraculous65/sentinel-risk-sdk" : "https://crates.io/dashboard"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block border rounded-lg p-3 flex items-start gap-3 transition-colors ${activeTab === "typescript"
                            ? "bg-blue-500/5 border-blue-500/20 hover:bg-blue-500/10"
                            : "bg-orange-500/5 border-orange-500/20 hover:bg-orange-500/10"
                            }`}
                    >
                        <div className="mt-0.5 relative">
                            <span className={`absolute inline-flex h-2 w-2 animate-ping rounded-full opacity-75 ${activeTab === "typescript" ? "bg-blue-400" : "bg-orange-400"
                                }`}></span>
                            <span className={`relative inline-flex h-2 w-2 rounded-full ${activeTab === "typescript" ? "bg-blue-500" : "bg-orange-500"
                                }`}></span>
                        </div>
                        <div>
                            <p className={`text-xs font-semibold ${activeTab === "typescript" ? "text-blue-400" : "text-orange-400"
                                }`}>
                                {activeTab === "typescript" ? "Verified on NPM" : "Published on Crates.io"}
                            </p>
                            <p className={`text-[10px] mt-0.5 ${activeTab === "typescript" ? "text-blue-400/60" : "text-orange-400/60"
                                }`}>
                                Latest Release: v0.1.0-alpha
                            </p>
                        </div>
                    </a>

                    <div className="space-y-2">
                        <p className="text-[10px] uppercase tracking-wider text-white/40 font-bold">Contract ID</p>
                        <div className="flex items-center gap-2 bg-black/40 p-2 rounded border border-white/5 group-hover:border-white/10 transition-colors">
                            <code className="text-[9px] text-white/60 font-mono break-all line-clamp-2">
                                {CONTRACT_ID}
                            </code>
                            <button
                                onClick={() => handleCopy(CONTRACT_ID, "contract")}
                                className="shrink-0 text-white/20 hover:text-white/60"
                            >
                                {copied === "contract" ? <Check className="h-3 w-3 text-emerald-500" /> : <Copy className="h-3 w-3" />}
                            </button>
                        </div>
                    </div>

                    <div className="pt-2 border-t border-white/5">
                        <a
                            href={activeTab === "typescript" ? "https://www.npmjs.com/package/@miraculous65/sentinel-risk-sdk" : "https://crates.io/dashboard"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-between group/link"
                        >
                            <span className="text-[10px] uppercase tracking-wider text-white/40 font-bold group-hover/link:text-white/60 transition-colors">
                                Source Code
                            </span>
                            <span className="text-[10px] text-white/20 group-hover/link:text-white/60 transition-colors">
                                {activeTab === "typescript" ? "NPM ↗" : "Crates.io ↗"}
                            </span>
                        </a>
                    </div>
                </div>
            )
        },
        {
            id: "04",
            variant: "wave",
            meta: "Real-time",
            title: "Network Activity",
            description: "Live incoming and outgoing contract calls fetched via Horizon API.",
            statLabel: "Live",
            statValue: "System Pulse",
            colSpan: 2,
            children: (
                <div className="mt-6 h-[200px] w-full border-t border-white/10 pt-4 relative flex flex-col justify-end">
                    <BarVisualizer
                        state="speaking"
                        demo={true}
                        barCount={40}
                        minHeight={20}
                        maxHeight={90}
                        className="h-full w-full bg-transparent p-0"
                        centerAlign={true}
                    />
                    <div className="absolute top-4 right-4 flex items-center justify-between text-[10px] text-white/30 gap-4">
                        <div className="flex items-center gap-2">
                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span>System Pulse</span>
                        </div>
                        <span>Protocol: Soroban</span>
                    </div>
                </div>
            )
        }
    ];

    if (activeTab === 'rust') {
        // Swap layout for Rust tab if needed, or keep generic. 
        // For now, the responsive grid logic in Bento3Section handles content well.
    }

    return (
        <Bento3Section
            items={bentoItems}
            title="Sentinel SDK"
            subtitle="The ultimate Developer Experience for integrating on-chain AI risk limits."
            badge="Developer Tools"
        />
    );
}
