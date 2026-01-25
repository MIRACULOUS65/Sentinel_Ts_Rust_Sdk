import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function MLEnginePage() {
    return (
        <div className="container py-10">
            <div className="mx-auto max-w-4xl space-y-8">

                {/* Header */}
                <div className="space-y-4">
                    <h1 className="text-4xl font-bold tracking-tight">AI/ML Engine</h1>
                    <p className="text-xl text-muted-foreground">
                        Autonomous behavioral analysis pipeline. Fetches data, trains models, and predicts wallet risk levels.
                    </p>
                    <div className="flex gap-4">
                        <Button asChild>
                            <Link href="https://github.com/sentinel-risk" target="_blank">View Models</Link>
                        </Button>
                    </div>
                </div>

                {/* Services Grid */}
                <div className="grid gap-6 md:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Service 1: Horizon Fetcher</CardTitle>
                            <CardDescription>Data Ingestion</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground mb-4">
                                Fetches real-time Stellar transaction data and tracks wallet frequencies.
                            </p>
                            <div className="bg-muted p-3 rounded text-xs font-mono">
                                GET /explorer/wallets/frequency
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle>Service 2: ML Model</CardTitle>
                            <CardDescription>Risk Analysis</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground mb-4">
                                Analyzes transaction patterns to assign risk scores (0-100) and decisions (Allow, Limit, Freeze).
                            </p>
                            <div className="bg-muted p-3 rounded text-xs font-mono">
                                POST /predict/risk
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Workflow */}
                <Card>
                    <CardHeader>
                        <CardTitle>Risk Pipeline</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center gap-4">
                                <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">1</div>
                                <div>
                                    <p className="font-medium">Data Collection</p>
                                    <p className="text-sm text-muted-foreground">Horizon Service monitors network activity.</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">2</div>
                                <div>
                                    <p className="font-medium">Analysis</p>
                                    <p className="text-sm text-muted-foreground">ML Engine processes behavior against trained models.</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">3</div>
                                <div>
                                    <p className="font-medium">Signing</p>
                                    <p className="text-sm text-muted-foreground">Oracle signs the risk score for on-chain usability.</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

            </div>
        </div>
    );
}
