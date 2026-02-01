"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

export function SiteFooter() {
    const pathname = usePathname();

    // Hide footer on the landing page
    if (pathname === "/") {
        return null;
    }

    return (
        <footer className="border-t border-neutral-200 dark:border-neutral-800 py-12 px-6 bg-white dark:bg-black text-black dark:text-white">
            <div className="max-w-7xl mx-auto">
                <div className="grid md:grid-cols-4 gap-8 mb-8">
                    <div>
                        <div className="flex items-center space-x-3 mb-4">
                            <Image
                                src="/sentinel-logo.jpeg"
                                alt="Sentinel"
                                width={36}
                                height={36}
                                className="rounded-lg"
                            />
                            <span className="font-bold text-lg tracking-tight">SENTINEL</span>
                        </div>
                        <p className="text-sm text-neutral-600 dark:text-neutral-400">
                            Autonomous AI Risk Engine for Stellar
                        </p>
                    </div>
                    <div>
                        <h4 className="font-bold mb-4">Product</h4>
                        <ul className="space-y-2 text-sm text-neutral-600 dark:text-neutral-400">
                            <li><a href="/features" className="hover:text-black dark:hover:text-white transition-colors">Features</a></li>
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">Pricing</a></li>
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">Security</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-bold mb-4">Developers</h4>
                        <ul className="space-y-2 text-sm text-neutral-600 dark:text-neutral-400">
                            <li><a href="/docs" className="hover:text-black dark:hover:text-white transition-colors">Documentation</a></li>
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">API Reference</a></li>
                            <li><a href="https://github.com/sentinel-risk" className="hover:text-black dark:hover:text-white transition-colors">GitHub</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-bold mb-4">Company</h4>
                        <ul className="space-y-2 text-sm text-neutral-600 dark:text-neutral-400">
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">About</a></li>
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">Blog</a></li>
                            <li><a href="#" className="hover:text-black dark:hover:text-white transition-colors">Contact</a></li>
                        </ul>
                    </div>
                </div>
                <div className="pt-8 border-t border-neutral-200 dark:border-neutral-800 text-center text-sm text-neutral-600 dark:text-neutral-400">
                    © 2026 Sentinel AI Risk Engine. Built for Stellar hackathon.
                </div>
            </div>
        </footer>
    );
}
