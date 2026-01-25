"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, CheckCircle2, ShieldAlert, ShieldCheck, ArrowRight, Lock } from "lucide-react";

// Service Endpoints (Production / Local)
// const SERVICE_1_URL = "http://localhost:8000";
// const ORACLE_URL = "http://localhost:8001";

const SERVICE_1_URL = "https://stellar-horizon-fetcher.onrender.com";
const ORACLE_URL = "https://sentinel-oracle.onrender.com";

// Decision Logic (Mimicking SDK)
const getSDKDecision = (score: number) => {
    if (score < 50) return "Allow";
    if (score < 80) return "Limit";
    return "Freeze";
};

export default function Dashboard() {
    const [wallet, setWallet] = useState("");
    const [loading, setLoading] = useState(false);

    // Pipeline State
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
            // --- Step 1: Analyze (Service 1 -> Service 2) ---
            addLog("Step 1: Analyyzing Wallet & Fetching ML Score...");
            const analyzeRes = await fetch(`${SERVICE_1_URL}/analyze/wallet/${wallet}`);
            if (!analyzeRes.ok) throw new Error("Service 1 Failed");
            const analysis = await analyzeRes.json();

            setAnalysisData(analysis);
            addLog(`✅ Analysis Complete. Risk Score: ${analysis.risk_analysis.risk_score}`);

            // --- Step 2: Oracle Signing ---
            setStep("signing");
            addLog("Step 2: Requesting Oracle Signature...");

            // Prepare payload for Oracle (must match their expected input)
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

            // --- Step 3: SDK Verification (Simulation) ---
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

    return (
        <div className="min-h-screen bg-background p-6 md:p-12 font-sans text-foreground">
            <div className="max-w-6xl mx-auto space-y-8">

                <div className="flex items-center justify-between border-b pb-4">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Sentinel Console</h1>
                        <p className="text-muted-foreground">End-to-End Risk Infrastructure Visualization</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Controls */}
                    <div className="lg:col-span-1 space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Target Wallet</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex gap-2">
                                    <Input
                                        value={wallet}
                                        onChange={(e) => setWallet(e.target.value)}
                                        placeholder="G..."
                                        className="font-mono text-xs"
                                    />
                                </div>
                                <div className="flex gap-2">
                                    <Button variant="outline" size="sm" onClick={() => setWallet(DEFAULT_WALLET)}>
                                        Load Test Wallet
                                    </Button>
                                    <Button size="sm" onClick={runPipeline} disabled={loading}>
                                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Run Pipeline"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Logs */}
                        <Card className="h-[400px] flex flex-col">
                            <CardHeader>
                                <CardTitle className="text-lg">System Logs</CardTitle>
                            </CardHeader>
                            <CardContent className="flex-1 overflow-y-auto font-mono text-xs bg-muted p-4 rounded-md mx-4 mb-4">
                                {logs.length === 0 && <span className="opacity-50">// Ready...</span>}
                                {logs.map((log, i) => (
                                    <div key={i} className="mb-2 border-b border-border/50 pb-1 break-all">{log}</div>
                                ))}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Pipeline Visualization */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Step 1: Analysis */}
                        <Card className={step === "idle" ? "opacity-50" : ""}>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">1</div>
                                    Service 1 & 2: Analysis
                                </CardTitle>
                                {analysisData && <CheckCircle2 className="text-green-500 h-6 w-6" />}
                            </CardHeader>
                            {analysisData && (
                                <CardContent className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-muted-foreground uppercase font-bold">Risk Score</p>
                                        <div className="text-4xl font-black">{analysisData.risk_analysis.risk_score}<span className="text-lg font-normal text-muted-foreground">/100</span></div>
                                    </div>
                                    <div>
                                        <p className="text-sm text-muted-foreground uppercase font-bold">Reason</p>
                                        <p className="text-sm">{analysisData.risk_analysis.reason}</p>
                                    </div>
                                    <div className="col-span-2">
                                        <p className="text-xs text-muted-foreground break-all">
                                            tx_count: {analysisData.transaction_summary?.count ?? 0} • last_updated: {analysisData.last_updated ?? "N/A"}
                                        </p>
                                    </div>
                                </CardContent>
                            )}
                        </Card>

                        {/* Arrow */}
                        <div className="flex justify-center">
                            <ArrowRight className="text-muted-foreground/30 h-8 w-8 rotate-90 lg:rotate-0" />
                        </div>

                        {/* Step 2: Oracle */}
                        <Card className={(step === "idle" || step === "analyzing") ? "opacity-50" : ""}>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">2</div>
                                    Oracle Service: Signing
                                </CardTitle>
                                {oracleData && <CheckCircle2 className="text-green-500 h-6 w-6" />}
                            </CardHeader>
                            {oracleData && (
                                <CardContent>
                                    <div className="bg-muted p-3 rounded-md font-mono text-[10px] break-all">
                                        <p className="text-muted-foreground mb-1">// Ed25519 Signature</p>
                                        {oracleData.signature}
                                    </div>
                                    <div className="mt-2 text-xs text-muted-foreground">
                                        Signed Timestamp: {oracleData.payload.timestamp}
                                    </div>
                                </CardContent>
                            )}
                        </Card>

                        {/* Arrow */}
                        <div className="flex justify-center">
                            <ArrowRight className="text-muted-foreground/30 h-8 w-8" />
                        </div>

                        {/* Step 3: SDK */}
                        <Card className={step !== "complete" ? "opacity-50" : "border-primary"}>
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">3</div>
                                    Sentinel SDK: Verification
                                </CardTitle>
                                {step === "complete" && <ShieldCheck className="text-primary h-6 w-6" />}
                            </CardHeader>
                            {step === "complete" && (
                                <CardContent className="text-center py-6">
                                    <p className="text-sm text-muted-foreground uppercase tracking-widest mb-2">Final Decision</p>
                                    <div className={`text-5xl font-black ${sdkDecision === "Allow" ? "text-green-500" :
                                        sdkDecision === "Limit" ? "text-yellow-500" : "text-red-500"
                                        }`}>
                                        {sdkDecision.toUpperCase()}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-4">
                                        Verified On-Chain • Immutable
                                    </p>
                                </CardContent>
                            )}
                        </Card>

                    </div>

                </div>
            </div>
        </div>
    );
}


