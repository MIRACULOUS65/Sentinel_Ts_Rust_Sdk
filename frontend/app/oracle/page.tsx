import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function OraclePage() {
    return (
        <div className="container py-10">
            <div className="mx-auto max-w-4xl space-y-8">

                {/* Header */}
                <div className="space-y-4">
                    <h1 className="text-4xl font-bold tracking-tight">Oracle Service</h1>
                    <p className="text-xl text-muted-foreground">
                        Cryptographic trust bridge using Ed25519 signatures. Connects our AI ML Engine to Soroban smart contracts.
                    </p>
                    <div className="flex gap-4">
                        <Button variant="outline" asChild>
                            <Link href="/docs/oracle">Read Architecture Docs</Link>
                        </Button>
                    </div>
                </div>

                {/* Architecture Diagram */}
                <Card>
                    <CardHeader>
                        <CardTitle>Architecture Flow</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md bg-muted p-4 text-center font-mono text-sm">
                            ML Engine → Oracle (Sign) → Soroban Contract (Verify) → Enforcement
                        </div>
                    </CardContent>
                </Card>

                {/* Key Features */}
                <div className="grid gap-6 md:grid-cols-3">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Cryptographic Trust</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                Uses Ed25519 signatures to ensure risk scores are authentic and haven't been tampered with.
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Replay Protection</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                Includes timestamps in signed payloads to prevent old risk scores from being reused maliciously.
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Mock & Real Data</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                Supports mock data for testing and seamless transition to real ML output without code changes.
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* API Info */}
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold">API Interfaces</h2>
                    <div className="grid gap-6 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base font-mono">POST /sign-risk</CardTitle>
                                <CardDescription>Signs a risk score payload.</CardDescription>
                            </CardHeader>
                            <CardContent className="bg-muted font-mono text-xs p-4">
                                {`{
  "wallet": "GABCD...",
  "risk_score": 87,
  "reason": "abnormal activity"
}`}
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base font-mono">GET /health</CardTitle>
                                <CardDescription>Service health check.</CardDescription>
                            </CardHeader>
                            <CardContent className="bg-muted font-mono text-xs p-4">
                                {`{
  "status": "healthy",
  "oracle_pubkey": "ed5f..."
}`}
                            </CardContent>
                        </Card>
                    </div>
                </div>

            </div>
        </div>
    );
}
