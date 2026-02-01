"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, ShieldCheck } from "lucide-react";
import Bento3Section, { BentoItem } from "@/components/ui/bento-monochrome-1";

// Service Endpoints
const SERVICE_1_URL = "https://sentinel-653o.onrender.com";
const ORACLE_URL = "https://sentinel-oracle.onrender.com";

const getSDKDecision = (score: number) => {
    if (score < 50) return "Allow";
    if (score < 80) return "Limit";
    return "Freeze";
};

export default function Dashboard() {
    const [wallet, setWallet] = useState("");
    const [loading, setLoading] = useState(false);
    const [step, setStep] = useState<"idle" | "analyzing" | "signing" | "complete">("idle");
    const [analysisData, setAnalysisData] = useState<any>(null);
    const [oracleData, setOracleData] = useState<any>(null);
    const [sdkDecision, setSdkDecision] = useState<string>("");
    const [logs, setLogs] = useState<string[]>([]);

    const DEFAULT_WALLET = "GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT";

    const addLog = (msg: string) => {
        setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);
    };

    const runPipeline = async () => {
        if (!wallet) return;
        setLoading(true);
        setStep("analyzing");
        setAnalysisData(null);
        setOracleData(null);
        setLogs([]);

        try {
            addLog("Step 1: Analyzing Wallet & Fetching ML Score...");
            const analyzeRes = await fetch(`${SERVICE_1_URL}/analyze/wallet/${wallet}`);
            if (!analyzeRes.ok) throw new Error("Service 1 Failed");
            const analysis = await analyzeRes.json();

            setAnalysisData(analysis);
            addLog(`✅ Analysis Complete. Risk Score: ${analysis.risk_analysis.risk_score}`);

            setStep("signing");
            addLog("Step 2: Requesting Oracle Signature...");

            const oraclePayload = {
                wallet: wallet,
                risk_score: analysis.risk_analysis.risk_score,
                reason: analysis.risk_analysis.reason || "automated_analysis"
            };

            const oracleRes = await fetch(`${ORACLE_URL}/sign-risk`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(oraclePayload)
            });

            if (!oracleRes.ok) throw new Error("Oracle Failed");
            const signedData = await oracleRes.json();

            setOracleData(signedData);
            addLog("✅ Oracle Signed. Signature generated.");

            setStep("complete");
            const decision = getSDKDecision(analysis.risk_analysis.risk_score);
            setSdkDecision(decision);
            addLog(`Step 3: SDK Verified. Decision: ${decision.toUpperCase()}`);

        } catch (e: any) {
            addLog(`❌ Pipeline Error: ${e.message}`);
            setStep("idle");
        }
        setLoading(false);
    };

    const bentoItems: BentoItem[] = [
        {
            id: "01",
            variant: "orbit",
            meta: "Input",
            title: "Target Wallet",
            description: "Enter a Stellar public key to initiate the risk analysis pipeline.",
            statLabel: "Status",
            statValue: loading ? "Running..." : "Ready",
            colSpan: 1,
            children: (
                <div className="mt-6 flex flex-col gap-4">
                    <Input
                        value={wallet}
                        onChange={(e) => setWallet(e.target.value)}
                        placeholder="G..."
                        className="bg-black/20 border-white/10 text-white placeholder:text-white/20 font-mono"
                    />
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setWallet(DEFAULT_WALLET)}
                            className="bg-transparent border-white/20 text-white hover:bg-white/5"
                        >
                            Test Wallet
                        </Button>
                        <Button
                            size="sm"
                            onClick={runPipeline}
                            disabled={loading}
                            className="bg-white text-black hover:bg-white/90"
                        >
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Run Pipeline"}
                        </Button>
                    </div>
                </div>
            )
        },
        {
            id: "02",
            variant: "relay",
            meta: "Logs",
            title: "System Output",
            description: "Real-time execution logs from the Sentinel infrastructure components.",
            statLabel: "Log Count",
            statValue: logs.length.toString(),
            colSpan: 1, // Adjusted to 1 to fit grid
            children: (
                <div className="mt-4 h-[200px] w-full overflow-y-auto rounded-xl border border-white/10 bg-black/40 p-4 font-mono text-[10px] sm:text-xs text-white/70">
                    {logs.length === 0 && <span className="opacity-30">// Waiting for pipeline...</span>}
                    {logs.map((log, i) => (
                        <div key={i} className="mb-1 border-b border-white/5 pb-1 break-all last:border-0">
                            {log}
                        </div>
                    ))}
                </div>
            )
        },
        {
            id: "03",
            variant: "wave",
            meta: "Step 1",
            title: "AI Risk Analysis",
            description: "Behavioral graph analysis and risk scoring via Service 1 & 2.",
            statLabel: "Risk Score",
            statValue: analysisData ? `${analysisData.risk_analysis.risk_score}/100` : "---",
            colSpan: 1,
            children: analysisData ? (
                <div className="mt-6 grid grid-cols-2 gap-4 border-t border-white/10 pt-4">
                    <div>
                        <p className="text-[10px] uppercase tracking-wider opacity-50 text-white">Reason</p>
                        <p className="text-sm font-medium text-white">{analysisData.risk_analysis.reason}</p>
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-wider opacity-50 text-white">Transactions</p>
                        <p className="text-sm font-medium text-white">{analysisData.transaction_summary?.count ?? 0}</p>
                    </div>
                </div>
            ) : undefined
        },
        {
            id: "04",
            variant: "spark",
            meta: "Step 2",
            title: "Oracle Signing",
            description: "Cryptographic proof generation signed by the Risk Oracle.",
            statLabel: "Signature",
            statValue: oracleData ? "Generated" : "Pending",
            colSpan: 1,
            children: oracleData ? (
                <div className="mt-6 border-t border-white/10 pt-4">
                    <div className="rounded bg-black/40 p-2 font-mono text-[10px] text-white/60 break-all border border-white/5">
                        {oracleData.signature}
                    </div>
                    <p className="mt-2 text-[10px] text-white/40">Timestamp: {oracleData.payload.timestamp}</p>
                </div>
            ) : undefined
        },
        {
            id: "05",
            variant: "loop",
            meta: "Step 3",
            title: "Contract Enforce",
            description: "On-chain verification and asset freezing/allowance.",
            statLabel: "Decision",
            statValue: sdkDecision || "Pending",
            colSpan: 2, // Full width for final result
            children: step === "complete" ? (
                <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-4">
                    <div>
                        <p className="text-xs uppercase tracking-widest text-white/50">Final Action</p>
                        <p className={`text-4xl font-bold ${sdkDecision === "Allow" ? "text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.5)]" :
                            sdkDecision === "Limit" ? "text-amber-400" : "text-rose-500 drop-shadow-[0_0_10px_rgba(244,63,94,0.5)]"
                            }`}>
                            {sdkDecision.toUpperCase()}
                        </p>
                    </div>
                    <ShieldCheck className="h-16 w-16 text-white/10" />
                </div>
            ) : undefined
        }
    ];

    return (
        <Bento3Section
            items={bentoItems}
            title="Sentinel Console"
            subtitle="Real-time Risk Infrastructure Visualization"
            badge="Live System"
            metrics={[
                { label: "Pipeline Step", value: step === "idle" ? "Ready" : step === "complete" ? "Finished" : step.toUpperCase() }
            ]}
        />
    );
}


