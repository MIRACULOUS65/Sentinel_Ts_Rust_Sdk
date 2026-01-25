"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Home() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-black/10 dark:border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black dark:bg-white rounded-md"></div>
            <span className="text-xl font-bold tracking-tight">SENTINEL</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-sm font-medium hover:opacity-60 transition-opacity">
              Dashboard
            </a>
            <a href="#" className="text-sm font-medium hover:opacity-60 transition-opacity">
              Analytics
            </a>
            <a href="#" className="text-sm font-medium hover:opacity-60 transition-opacity">
              Docs
            </a>
            <Link href="/dashboard">
              <Button variant="default" className="bg-black dark:bg-white text-white dark:text-black">
                Launch Console
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div
            className="text-center space-y-8"
            style={{
              transform: `translateY(${scrollY * 0.2}px)`,
              transition: "transform 0.1s ease-out",
            }}
          >
            {/* Animated background grid */}
            <div className="absolute inset-0 -z-10">
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#00000008_1px,transparent_1px),linear-gradient(to_bottom,#00000008_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
            </div>

            <div className="inline-block">
              <span className="text-sm font-semibold tracking-wider uppercase border border-black/20 dark:border-white/20 px-4 py-2 rounded-full">
                Autonomous AI Risk Engine
              </span>
            </div>

            <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none">
              <span className="block bg-gradient-to-br from-black to-black/40 dark:from-white dark:to-white/40 bg-clip-text text-transparent">
                Real-Time
              </span>
              <span className="block">Fraud Prevention</span>
              <span className="block bg-gradient-to-br from-black to-black/40 dark:from-white dark:to-white/40 bg-clip-text text-transparent">
                for Stellar
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-black/60 dark:text-white/60 max-w-3xl mx-auto leading-relaxed">
              AI-powered behavioral analysis meets on-chain enforcement.
              Detect abnormal wallet activity and enforce security
              autonomously through Soroban smart contracts.
            </p>

            <div className="flex items-center justify-center gap-4 pt-4">
              <Link href="/dashboard">
                <Button
                  size="lg"
                  className="bg-black dark:bg-white text-white dark:text-black text-lg px-8 py-6 hover:opacity-80 transition-all"
                >
                  Launch Console
                </Button>
              </Link>
              <Button
                size="lg"
                variant="outline"
                className="border-2 border-black dark:border-white text-lg px-8 py-6 hover:bg-black/5 dark:hover:bg-white/5 transition-all"
              >
                View Demo
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 pt-16 max-w-4xl mx-auto">
              <div className="space-y-2">
                <div className="text-4xl font-black">99.8%</div>
                <div className="text-sm text-black/60 dark:text-white/60 uppercase tracking-wide">
                  Detection Rate
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-4xl font-black">&lt;3s</div>
                <div className="text-sm text-black/60 dark:text-white/60 uppercase tracking-wide">
                  Response Time
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-4xl font-black">24/7</div>
                <div className="text-sm text-black/60 dark:text-white/60 uppercase tracking-wide">
                  Autonomous
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-black/[0.02] dark:bg-white/[0.02]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-black mb-4">
              Complete Protection Pipeline
            </h2>
            <p className="text-lg text-black/60 dark:text-white/60 max-w-2xl mx-auto">
              From detection to enforcement, fully automated and cryptographically secure
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: "AI Detection",
                description: "Unsupervised anomaly detection using behavioral graph analysis",
                icon: "🧠",
              },
              {
                title: "Cryptographic Oracle",
                description: "Ed25519 signatures bridge AI predictions to blockchain trust",
                icon: "🔐",
              },
              {
                title: "Smart Contracts",
                description: "Soroban contracts enforce security rules autonomously on-chain",
                icon: "⚡",
              },
              {
                title: "Live Dashboard",
                description: "Real-time visualization of threats and enforcement actions",
                icon: "📊",
              },
            ].map((feature, i) => (
              <Card
                key={i}
                className="p-6 border-2 border-black/10 dark:border-white/10 bg-white dark:bg-black hover:border-black/20 dark:hover:border-white/20 transition-all hover:shadow-xl group"
              >
                <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-black/60 dark:text-white/60 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-black mb-4">
              Closed-Loop Security
            </h2>
            <p className="text-lg text-black/60 dark:text-white/60">
              End-to-end autonomous protection in &lt;5 seconds
            </p>
          </div>

          <div className="relative">
            {/* Flow visualization */}
            <div className="grid md:grid-cols-5 gap-4">
              {[
                { step: "01", label: "Transaction" },
                { step: "02", label: "AI Analysis" },
                { step: "03", label: "Oracle Sign" },
                { step: "04", label: "On-Chain" },
                { step: "05", label: "Enforce" },
              ].map((item, i) => (
                <div key={i} className="relative">
                  <Card className="p-6 text-center border-2 border-black/10 dark:border-white/10 hover:border-black dark:hover:border-white transition-all">
                    <div className="text-5xl font-black text-black/10 dark:text-white/10 mb-2">
                      {item.step}
                    </div>
                    <div className="font-semibold">{item.label}</div>
                  </Card>
                  {i < 4 && (
                    <div className="hidden md:block absolute top-1/2 -right-2 transform -translate-y-1/2 text-2xl">
                      →
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-black dark:bg-white">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-4xl md:text-6xl font-black text-white dark:text-black">
            Ready to Secure Your Network?
          </h2>
          <p className="text-xl text-white/80 dark:text-black/80">
            Deploy autonomous fraud prevention in minutes
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button
              size="lg"
              className="bg-white dark:bg-black text-black dark:text-white text-lg px-8 py-6 hover:opacity-80 transition-all"
            >
              Start Free Trial
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-2 border-white dark:border-black text-white dark:text-black text-lg px-8 py-6 hover:bg-white/10 dark:hover:bg-black/10 transition-all"
            >
              Contact Sales
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black/10 dark:border-white/10 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-6 h-6 bg-black dark:bg-white rounded"></div>
                <span className="font-bold">SENTINEL</span>
              </div>
              <p className="text-sm text-black/60 dark:text-white/60">
                Autonomous AI Risk Engine for Stellar
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-black/60 dark:text-white/60">
                <li><a href="#" className="hover:text-black dark:hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Developers</h4>
              <ul className="space-y-2 text-sm text-black/60 dark:text-white/60">
                <li><a href="#" className="hover:text-black dark:hover:text-white">Documentation</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">API Reference</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">GitHub</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-black/60 dark:text-white/60">
                <li><a href="#" className="hover:text-black dark:hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-black dark:hover:text-white">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-black/10 dark:border-white/10 text-center text-sm text-black/60 dark:text-white/60">
            © 2026 Sentinel AI Risk Engine. Built for Stellar hackathon.
          </div>
        </div>
      </footer>
    </div>
  );
}
