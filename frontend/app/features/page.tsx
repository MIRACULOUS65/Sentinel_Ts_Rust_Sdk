"use client";

import { CardBody, CardContainer, CardItem } from "@/components/ui/3d-card";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function FeaturesPage() {
    const features = [
        {
            title: "Live Stellar Transactions",
            description: "Real-time monitoring and visualization of every transaction on the Stellar network.",
            icon: "⚡",
            metric: "1500+ TPS",
        },
        {
            title: "AI Risk Scores",
            description: "Autonomous behavioral analysis assigning risk scores (0-100) to every wallet.",
            icon: "🧠",
            metric: "99.8% Accuracy",
        },
        {
            title: "Wallet Graphs",
            description: "Interactive network graph showing fund flow relationships and clustering.",
            icon: "🕸️",
            metric: "Deep Analysis",
        },
        {
            title: "On-Chain Enforcement",
            description: "Smart contracts automatically freeze or limit high-risk wallets via Oracle proof.",
            icon: "🔒",
            metric: "<3s Response",
        },
    ];

    return (
        <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white p-6">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 w-full z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-black/10 dark:border-white/10">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center space-x-2 group">
                        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        <span className="font-bold">Back to Home</span>
                    </Link>
                    <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-black dark:bg-white rounded-md"></div>
                        <span className="font-bold tracking-tight">SENTINEL</span>
                    </div>
                </div>
            </nav>

            <div className="pt-32 pb-20 max-w-7xl mx-auto">
                <div className="text-center mb-16 space-y-4">
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter">
                        Core Features
                    </h1>
                    <p className="text-xl text-black/60 dark:text-white/60 max-w-2xl mx-auto">
                        A complete autonomous security pipeline
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4">
                    {features.map((feature, idx) => (
                        <CardContainer key={idx} className="inter-var w-full">
                            <CardBody className="bg-white dark:bg-black relative group/card dark:hover:shadow-2xl dark:hover:shadow-white/[0.1] hover:shadow-2xl hover:shadow-black/[0.1] border-black/10 dark:border-white/10 w-full h-auto rounded-xl p-8 border-2">
                                <CardItem
                                    translateZ="50"
                                    className="text-6xl mb-6 font-bold text-neutral-600 dark:text-white"
                                >
                                    {feature.icon}
                                </CardItem>
                                <CardItem
                                    as="p"
                                    translateZ="60"
                                    className="text-neutral-500 text-sm max-w-sm mt-2 dark:text-neutral-300"
                                >
                                    FEATURE {idx + 1}
                                </CardItem>
                                <CardItem
                                    as="h3"
                                    translateZ="50"
                                    className="text-3xl font-black text-neutral-600 dark:text-white mt-4"
                                >
                                    {feature.title}
                                </CardItem>
                                <CardItem
                                    as="p"
                                    translateZ="60"
                                    className="text-neutral-500 text-lg max-w-sm mt-4 dark:text-neutral-300 leading-relaxed"
                                >
                                    {feature.description}
                                </CardItem>
                                <div className="mt-10 flex justify-between items-center">
                                    <CardItem
                                        translateZ={20}
                                        as="div"
                                        className="px-4 py-2 rounded-xl text-xs font-normal dark:text-white border border-black/10 dark:border-white/10"
                                    >
                                        {feature.metric}
                                    </CardItem>
                                    <CardItem
                                        translateZ={20}
                                        as="button"
                                        className="px-4 py-2 rounded-xl bg-black dark:bg-white text-white dark:text-black text-xs font-bold hover:opacity-80 transition-opacity"
                                    >
                                        Learn More →
                                    </CardItem>
                                </div>
                            </CardBody>
                        </CardContainer>
                    ))}
                </div>
            </div>
        </div>
    );
}
