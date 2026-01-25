import Bento3Section, { BentoItem } from "@/components/ui/bento-monochrome-1";
import { ArrowRight, Activity, Database, BrainCircuit } from "lucide-react";

export default function MLEnginePage() {
    const bentoItems: BentoItem[] = [
        {
            id: "01",
            variant: "orbit",
            meta: "Data Ingestion",
            title: "Horizon Fetcher Service",
            description: "Fetches real-time Stellar transaction data and tracks wallet frequencies. Acts as the dedicated data layer for the risk pipeline.",
            statLabel: "Endpoint",
            statValue: "GET /frequency",
            colSpan: 1,
            children: (
                <div className="mt-6 border-t border-white/10 pt-4">
                    <div className="flex items-center gap-2 text-xs font-mono text-white/50 mb-2">
                        <Database className="h-3 w-3" />
                        <span>Data Source</span>
                    </div>
                    <p className="text-sm text-white/80">Stellar Horizon API</p>
                </div>
            )
        },
        {
            id: "02",
            variant: "spark",
            meta: "Risk Analysis",
            title: "ML Risk Engine",
            description: "Analyzes transaction patterns to assign risk scores (0-100) and decisions (Allow, Limit, Freeze) using a pre-trained Isolation Forest model.",
            statLabel: "Endpoint",
            statValue: "POST /predict",
            colSpan: 1,
            children: (
                <div className="mt-6 border-t border-white/10 pt-4">
                    <div className="flex items-center gap-2 text-xs font-mono text-white/50 mb-2">
                        <BrainCircuit className="h-3 w-3" />
                        <span>Model Type</span>
                    </div>
                    <p className="text-sm text-white/80">Isolation Forest (Unsupervised)</p>
                </div>
            )
        },
        {
            id: "03",
            variant: "relay",
            meta: "Workflow",
            title: "Autonomous Pipeline",
            description: "The complete journey of a risk assessment request, from raw data to signed cryptographic proof.",
            statLabel: "Stages",
            statValue: "3 Steps",
            colSpan: 2,
            children: (
                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="group relative rounded-xl bg-white/5 p-4 border border-white/5 hover:border-white/10 transition-colors">
                        <div className="absolute top-4 right-4 text-xs font-bold text-white/20">01</div>
                        <div className="mb-2 h-8 w-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                            <Activity className="h-4 w-4" />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Collection</h4>
                        <p className="text-xs text-white/50 mt-1">Horizon service monitors network activity.</p>
                    </div>

                    <div className="hidden md:flex items-center justify-center">
                        <ArrowRight className="text-white/20" />
                    </div>

                    <div className="group relative rounded-xl bg-white/5 p-4 border border-white/5 hover:border-white/10 transition-colors">
                        <div className="absolute top-4 right-4 text-xs font-bold text-white/20">02</div>
                        <div className="mb-2 h-8 w-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
                            <BrainCircuit className="h-4 w-4" />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Analysis</h4>
                        <p className="text-xs text-white/50 mt-1">Engine processes behavior against models.</p>
                    </div>

                    <div className="hidden md:flex items-center justify-center">
                        <ArrowRight className="text-white/20" />
                    </div>

                    <div className="group relative rounded-xl bg-white/5 p-4 border border-white/5 hover:border-white/10 transition-colors">
                        <div className="absolute top-4 right-4 text-xs font-bold text-white/20">03</div>
                        <div className="mb-2 h-8 w-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400">
                            <Database className="h-4 w-4" />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Signing</h4>
                        <p className="text-xs text-white/50 mt-1">Oracle signs the risk score for chain.</p>
                    </div>
                </div>
            )
        }
    ];

    return (
        <Bento3Section
            items={bentoItems}
            title="AI/ML Engine"
            subtitle="Autonomous behavioral analysis pipeline. Fetches data, trains models, and predicts wallet risk levels."
            badge="Core System"
        />
    );
}
