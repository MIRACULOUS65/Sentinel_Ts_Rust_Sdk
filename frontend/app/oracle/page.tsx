import Bento3Section, { BentoItem } from "@/components/ui/bento-monochrome-1";
import { ArrowRight, ShieldCheck, Clock } from "lucide-react";

export default function OraclePage() {
    const bentoItems: BentoItem[] = [
        {
            id: "01",
            variant: "relay",
            meta: "Architecture",
            title: "Trust Bridge Flow",
            description: "Securely bridging off-chain ML insights to on-chain Soroban smart contracts via cryptographic proofs.",
            statLabel: "Type",
            statValue: "Generic Oracle",
            colSpan: 2,
            children: (
                <div className="mt-8 flex flex-col md:flex-row items-center gap-4 justify-between bg-white/5 rounded-xl p-6 border border-white/5">
                    <span className="text-sm font-mono text-white/70">ML Engine</span>
                    <ArrowRight className="h-4 w-4 text-white/30 rotate-90 md:rotate-0" />
                    <div className="flex flex-col items-center">
                        <span className="text-sm font-bold text-white bg-white/10 px-3 py-1 rounded-full border border-white/10">Oracle (Sign)</span>
                    </div>
                    <ArrowRight className="h-4 w-4 text-white/30 rotate-90 md:rotate-0" />
                    <span className="text-sm font-mono text-white/70">Soroban Contract</span>
                    <ArrowRight className="h-4 w-4 text-white/30 rotate-90 md:rotate-0" />
                    <span className="text-sm font-bold text-white">Enforcement</span>
                </div>
            )
        },
        {
            id: "02",
            variant: "orbit",
            meta: "Security",
            title: "Cryptographic Trust",
            description: "Uses Ed25519 signatures to ensure risk scores are authentic and haven't been tampered with in transit.",
            statLabel: "Curve",
            statValue: "Ed25519",
            colSpan: 1,
            children: (
                <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-4">
                    <ShieldCheck className="h-5 w-5 text-emerald-400" />
                    <span className="text-sm text-white/80">Verifiable On-Chain</span>
                </div>
            )
        },
        {
            id: "03",
            variant: "loop",
            meta: "Safety",
            title: "Replay Protection",
            description: "Includes precise timestamps in signed payloads. Old signatures are automatically rejected by the contracts.",
            statLabel: "Window",
            statValue: "30s",
            colSpan: 1,
            children: (
                <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-4">
                    <Clock className="h-5 w-5 text-amber-400" />
                    <span className="text-sm text-white/80">Timestamp Enforced</span>
                </div>
            )
        },
        {
            id: "04",
            variant: "spark",
            meta: "Integration",
            title: "API Interfaces",
            description: "Simple REST endpoints for internal services to request signatures.",
            statLabel: "Format",
            statValue: "JSON",
            colSpan: 2,
            children: (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="rounded-lg bg-black/40 p-4 border border-white/5 font-mono text-[10px] text-white/70">
                        <div className="mb-2 text-white/40 uppercase tracking-widest text-[9px]">POST /sign-risk</div>
                        <pre>{`{
  "wallet": "GABCD...",
  "risk_score": 87,
  "reason": "abnormal"
}`}</pre>
                    </div>
                    <div className="rounded-lg bg-black/40 p-4 border border-white/5 font-mono text-[10px] text-white/70">
                        <div className="mb-2 text-white/40 uppercase tracking-widest text-[9px]">Response</div>
                        <pre>{`{
  "signature": "3f8a...",
  "payload": { ... }
}`}</pre>
                    </div>
                </div>
            )
        }
    ];

    return (
        <Bento3Section
            items={bentoItems}
            title="Oracle Service"
            subtitle="Cryptographic trust bridge using Ed25519 signatures. Connects our AI ML Engine to Soroban smart contracts."
            badge="Security Layer"
        />
    );
}
