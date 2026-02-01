"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Link from "next/link";
import { useEffect, useState } from "react";
import Beams from "@/components/ui/beams";

export default function Home() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="relative min-h-screen w-full bg-neutral-950 overflow-hidden text-white selection:bg-neutral-800">

      {/* 3D Beams Background */}
      <div className="absolute inset-0 z-0 pointer-events-none grayscale opacity-80">
        <Beams rotation={-45} beamWidth={3} beamHeight={40} beamNumber={30} scale={0.3} />
      </div>

      {/* Hero Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 text-center">

        {/* Premium Badge */}
        <div className="mb-8 opacity-0 animate-fade-in-up" style={{ animationDelay: "0.2s", animationFillMode: "forwards" }}>
          <div className="inline-flex items-center px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md shadow-[0_0_15px_-3px_rgba(255,255,255,0.1)]">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2 animate-pulse"></div>
            <span className="text-xs font-semibold tracking-widest uppercase text-white/90">
              Autonomous AI Risk Engine
            </span>
          </div>
        </div>

        {/* Premium Title */}
        <h1 className="max-w-5xl text-6xl md:text-8xl font-bold tracking-tighter mb-8 leading-[1.05] opacity-0 animate-fade-in-up mix-blend-screen" style={{ animationDelay: "0.4s", animationFillMode: "forwards" }}>
          <span className="inline-block text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/50 pb-2">
            Real-Time
          </span>
          <br />
          <span className="inline-block text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/50 pb-2">
            Fraud Prevention
          </span>
        </h1>

        {/* Premium Description */}
        <p className="max-w-2xl text-lg md:text-xl text-neutral-400/90 mb-12 leading-relaxed opacity-0 animate-fade-in-up font-light tracking-wide" style={{ animationDelay: "0.6s", animationFillMode: "forwards" }}>
          AI-powered behavioral analysis meets on-chain enforcement.
          <br className="hidden md:block" />
          Secure your network autonomously with Soroban.
        </p>

        {/* Premium Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-5 opacity-0 animate-fade-in-up" style={{ animationDelay: "0.8s", animationFillMode: "forwards" }}>
          <Link href="/dashboard">
            <button className="group relative h-14 px-8 rounded-full bg-white text-black font-bold text-base tracking-wide overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)]">
              <span className="relative z-10 flex items-center gap-2">
                Launch Console
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 transition-transform group-hover:translate-x-0.5">
                  <path d="M8.14645 3.14645C8.34171 2.95118 8.65829 2.95118 8.85355 3.14645L12.8536 7.14645C13.0488 7.34171 13.0488 7.65829 12.8536 7.85355L8.85355 11.8536C8.65829 12.0488 8.34171 12.0488 8.14645 11.8536C7.95118 11.6583 7.95118 11.3417 8.14645 11.1464L11.2929 8H2.5C2.22386 8 2 7.77614 2 7.5C2 7.22386 2.22386 7 2.5 7H11.2929L8.14645 3.85355C7.95118 3.65829 7.95118 3.34171 8.14645 3.14645Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
                </svg>
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent translate-x-[-100%] group-hover:animate-shine" />
            </button>
          </Link>

          <Link href="/features">
            <button className="h-14 px-8 rounded-full border border-white/20 bg-white/5 text-white font-semibold text-base tracking-wide backdrop-blur-md transition-all hover:bg-white/10 hover:border-white/30 hover:scale-105">
              Explore Features
            </button>
          </Link>
        </div>

      </div>

      {/* CSS for simple fade-in animation */}
      <style jsx global>{`
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
