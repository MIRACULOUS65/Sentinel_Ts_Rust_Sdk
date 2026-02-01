"use client";

import React from "react";
import MagicBento from "@/components/ui/magic-bento";

export default function HowItWorksPage() {
    const securityFlowCards = [
        {
            color: "#0a0a0a",
            title: "Transaction",
            description: "User initiates a Soroban transaction on the Stellar network.",
            label: "01"
        },
        {
            color: "#0a0a0a",
            title: "AI Analysis",
            description: "Risk Engine analyzes behavioral graph in <200ms.",
            label: "02"
        },
        {
            color: "#0a0a0a",
            title: "Oracle Sign",
            description: "Validators generate Ed25519 threshold signature.",
            label: "03"
        },
        {
            color: "#0a0a0a",
            title: "On-Chain",
            description: "Smart contract verifies the Oracle proof on-chain.",
            label: "04"
        },
        {
            color: "#0a0a0a",
            title: "Enforce",
            description: "Asset is automatically frozen or transaction allowed.",
            label: "05"
        },
        {
            color: "#0a0a0a",
            title: "Dashboard",
            description: "Live updates streamed to the admin console.",
            label: "06"
        }
    ];

    return (
        <div className="min-h-screen bg-black pt-24 px-4 pb-32 flex flex-col items-center">
            <div className="text-center mb-16 max-w-3xl">
                <h1 className="text-4xl md:text-7xl font-bold text-white mb-6">
                    Closed-Loop Security
                </h1>
                <p className="text-lg text-neutral-400">
                    End-to-end autonomous protection in &lt;5 seconds. Sentinel secures your network without human intervention.
                </p>
            </div>

            <div className="w-full max-w-6xl">
                <MagicBento
                    cards={securityFlowCards}
                    enableStars={true}
                    enableSpotlight={true}
                    enableBorderGlow={true}
                    enableTilt={true}
                    glowColor="255, 255, 255"
                />
            </div>
        </div>
    );
}
