import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function SDKPage() {
    return (
        <div className="container py-10">
            <div className="mx-auto max-w-4xl space-y-8">

                {/* Header */}
                <div className="space-y-4">
                    <h1 className="text-4xl font-bold tracking-tight">Sentinel SDK</h1>
                    <p className="text-xl text-muted-foreground">
                        On-chain risk enforcement SDK for Stellar protocols. Integrate AI-verified risk decisions directly into your smart contracts.
                    </p>
                    <div className="flex gap-4">
                        <Button asChild>
                            <Link href="https://github.com/sentinel-risk" target="_blank">View on GitHub</Link>
                        </Button>
                        <Button variant="outline" asChild>
                            <Link href="/docs">Read Docs</Link>
                        </Button>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid gap-6 md:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>What It Is</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">
                                Infrastructure, not an app. Sentinel provides an on-chain risk API that acts like Chainlink for risk data.
                                It enables programmable fraud prevention for any Stellar protocol.
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle>Key Principle</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">
                                <strong>Sentinel decides, protocols enforce.</strong> <br />
                                Your protocol queries the SDK for permission, receives a decision (Allow, Limit, Freeze), and enforces it.
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* Integration Code */}
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold">Integration Example</h2>
                    <Card className="bg-muted">
                        <CardContent className="p-6 font-mono text-sm overflow-x-auto">
                            {`use sentinel_sdk::SentinelSDKClient;

// In your protocol's contract
let sentinel = SentinelSDKClient::new(&env, &sentinel_contract_id);

match sentinel.check_permission(&user_wallet) {
    RiskDecision::Allow => {
        // Proceed with transaction
        self.execute_transfer(from, to, amount)
    },
    RiskDecision::Limit(max_amount) => {
        if amount > max_amount {
            panic!("Transaction exceeds risk limit");
        }
        self.execute_transfer(from, to, amount)
    },
    RiskDecision::Freeze => {
        panic!("Wallet blocked by Sentinel risk engine");
    }
}`}
                        </CardContent>
                    </Card>
                </div>

                {/* Deployment Info */}
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold">Deployment</h2>
                    <Card>
                        <CardHeader>
                            <CardTitle>Testnet Deployment</CardTitle>
                            <CardDescription>Deploy the contract and initialize with the Oracle public key.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="bg-muted p-4 rounded-md font-mono text-xs">
                                stellar contract deploy --wasm target/wasm32-unknown-unknown/release/sentinel_sdk.wasm ...
                            </div>
                        </CardContent>
                    </Card>
                </div>

            </div>
        </div>
    );
}
