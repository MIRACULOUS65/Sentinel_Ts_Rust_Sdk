"use client";

import React from "react";
import { Timeline } from "@/components/ui/timeline";
import { motion } from "framer-motion";

const PremiumCard = ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className={`p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm hover:bg-white/10 hover:border-white/20 transition-all shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] ${className}`}
    >
        {children}
    </motion.div>
);

export default function FeaturesPage() {
    const data = [
        {
            title: "Data Ingestion",
            content: (
                <div>
                    <p className="text-neutral-300 text-sm md:text-base font-normal mb-8 leading-relaxed">
                        Real-time ingestion of Stellar ledger events, transaction graphs, and wallet histories through a high-throughput pipeline.
                    </p>
                    <div className="grid grid-cols-2 gap-4">
                        <PremiumCard className="relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                                <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                            </div>
                            <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl mb-4 shadow-lg flex items-center justify-center text-2xl">⚡</div>
                            <div className="text-base font-bold text-white mb-1">Ledger Events</div>
                            <div className="text-xs text-neutral-400">Streaming raw tx data</div>
                        </PremiumCard>
                        <PremiumCard className="relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                                <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
                            </div>
                            <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl mb-4 shadow-lg flex items-center justify-center text-2xl">🌊</div>
                            <div className="text-base font-bold text-white mb-1">Mempool</div>
                            <div className="text-xs text-neutral-400">Pre-consensus monitoring</div>
                        </PremiumCard>
                    </div>
                </div>
            ),
        },
        {
            title: "AI Analysis",
            content: (
                <div>
                    <p className="text-neutral-300 text-sm md:text-base font-normal mb-8 leading-relaxed">
                        Behavioral graph analysis using Graph Neural Networks (GNNs) to detect anomalous patterns, sybil clusters, and laundering attempts.
                    </p>
                    <div className="grid grid-cols-1 gap-4">
                        <PremiumCard className="flex items-center gap-6">
                            <div className="relative">
                                <div className="h-20 w-20 rounded-full border-4 border-red-500/30 flex items-center justify-center">
                                    <span className="text-2xl font-black text-white">98%</span>
                                </div>
                                <div className="absolute inset-0 border-4 border-red-500 rounded-full border-t-transparent animate-spin duration-3000"></div>
                            </div>
                            <div>
                                <div className="text-xl font-bold text-white mb-1">Risk Score Engine</div>
                                <div className="text-sm text-neutral-400 mb-2">Real-time inference latency &lt; 200ms</div>
                                <div className="flex gap-2">
                                    <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-mono">HIGH_SEVERITY</span>
                                    <span className="px-2 py-1 rounded bg-neutral-800 text-neutral-400 text-xs font-mono">GNN_MODEL_V2</span>
                                </div>
                            </div>
                        </PremiumCard>
                    </div>
                </div>
            ),
        },
        {
            title: "Consensus",
            content: (
                <div>
                    <p className="text-neutral-300 text-sm md:text-base font-normal mb-8 leading-relaxed">
                        Sentinel validators independently verify the risk score and sign the assessment using threshold cryptography (Ed25519).
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <PremiumCard className="bg-neutral-900/50">
                            <div className="font-mono text-xs text-neutral-500 mb-2 uppercase tracking-wider">Validator Signature</div>
                            <div className="font-mono text-xs text-emerald-400 break-all bg-black/50 p-3 rounded border border-white/5">
                                0x8a7f3b2c1d4e5f6a7b8c9d0e1f2a3b4c...
                            </div>
                        </PremiumCard>
                        <PremiumCard className="bg-neutral-900/50">
                            <div className="font-mono text-xs text-neutral-500 mb-2 uppercase tracking-wider">Public Key</div>
                            <div className="font-mono text-xs text-blue-400 break-all bg-black/50 p-3 rounded border border-white/5">
                                GDAX...72H2
                            </div>
                        </PremiumCard>
                    </div>
                </div>
            ),
        },
        {
            title: "Enforcement",
            content: (
                <div>
                    <p className="text-neutral-300 text-sm md:text-base font-normal mb-8 leading-relaxed">
                        Soroban smart contracts autonomously execute security rules based on the Oracle's signed proof, blocking threats instantly.
                    </p>
                    <div className="grid grid-cols-2 gap-4">
                        <PremiumCard className="!bg-red-500/10 !border-red-500/30 hover:!bg-red-500/20">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></div>
                                <div className="font-bold text-red-400">Freeze Asset</div>
                            </div>
                            <div className="text-xs text-red-300/80">
                                Target wallet frozen due to confirmed phishing inputs.
                            </div>
                        </PremiumCard>
                        <PremiumCard className="!bg-emerald-500/10 !border-emerald-500/30 hover:!bg-emerald-500/20">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
                                <div className="font-bold text-emerald-400">Allow Tx</div>
                            </div>
                            <div className="text-xs text-emerald-300/80">
                                Transaction verified safe by 3/5 threshold.
                            </div>
                        </PremiumCard>
                    </div>
                </div>
            ),
        },
    ];

    return (
        <div className="w-full">
            <Timeline data={data} />
        </div>
    );
}
