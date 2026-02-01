"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
    Home,
    Shield,
    Zap,
    Book,
    LayoutDashboard,
    Terminal,
} from "lucide-react";

import { cn } from "@/lib/utils";

// Adapted for Sentinel App
const navItems = [
    { label: "Home", icon: Home, href: "/" },
    { label: "Features", icon: Shield, href: "/features" },
    { label: "How it Works", icon: Zap, href: "/how-it-works" },
    { label: "Console", icon: LayoutDashboard, href: "/dashboard" },
];

type BottomNavBarProps = {
    className?: string;
    defaultIndex?: number;
    stickyBottom?: boolean;
};

const consoleItems = [
    { label: "Home", icon: Home, href: "/" },
    { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
    { label: "Oracle", icon: Shield, href: "/oracle" },
    { label: "ML Engine", icon: Zap, href: "/ml-engine" },
    { label: "SDK", icon: Terminal, href: "/sdk" },
];

export function BottomNavBar({
    className,
    defaultIndex = 0,
    stickyBottom = true, // Default to true as per typical usage
}: BottomNavBarProps) {
    const pathname = usePathname();
    const [activeIndex, setActiveIndex] = useState(defaultIndex);

    const isConsole = ["/dashboard", "/oracle", "/ml-engine", "/sdk"].some(path => pathname?.startsWith(path));
    const items = isConsole ? consoleItems : navItems;

    useEffect(() => {
        const index = items.findIndex(item => item.href === pathname);
        if (index !== -1) {
            setActiveIndex(index);
        }
    }, [pathname, items]);

    return (
        <div className={cn(
            "flex justify-center w-full pointer-events-none", // Container to center it
            stickyBottom && "fixed inset-x-0 bottom-6 z-50"
        )}>
            <motion.nav
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 26 }}
                role="navigation"
                aria-label="Bottom Navigation"
                className={cn(
                    "pointer-events-auto bg-black/80 dark:bg-neutral-900/80 backdrop-blur-md border border-white/10 dark:border-white/10 rounded-full flex items-center p-2 shadow-2xl space-x-1 h-[58px]",
                    className
                )}
            >
                {items.map((item, idx) => {
                    const Icon = item.icon;
                    const isActive = activeIndex === idx;

                    return (
                        <Link key={item.label} href={item.href}>
                            <motion.button
                                whileTap={{ scale: 0.97 }}
                                className={cn(
                                    "flex items-center gap-0 px-3 py-2 rounded-full transition-colors duration-200 relative h-10 min-w-[44px] min-h-[40px] max-h-[44px]",
                                    isActive
                                        ? "bg-white text-black" // High contrast active state
                                        : "bg-transparent text-neutral-400 hover:text-white hover:bg-white/10",
                                    "focus:outline-none focus-visible:ring-0"
                                )}
                                onClick={() => setActiveIndex(idx)}
                                aria-label={item.label}
                                type="button"
                            >
                                <Icon
                                    size={20}
                                    strokeWidth={2.5}
                                    aria-hidden
                                    className="transition-colors duration-200"
                                />

                                <motion.div
                                    initial={false}
                                    animate={{
                                        width: isActive ? "auto" : "0px",
                                        opacity: isActive ? 1 : 0,
                                        marginLeft: isActive ? "8px" : "0px",
                                    }}
                                    transition={{
                                        width: { type: "spring", stiffness: 350, damping: 32 },
                                        opacity: { duration: 0.19 },
                                        marginLeft: { duration: 0.19 },
                                    }}
                                    className={cn("overflow-hidden flex items-center")}
                                >
                                    <span
                                        className={cn(
                                            "font-bold text-sm whitespace-nowrap select-none transition-opacity duration-200 pr-2",
                                            isActive ? "text-black" : "opacity-0"
                                        )}
                                        title={item.label}
                                    >
                                        {item.label}
                                    </span>
                                </motion.div>
                            </motion.button>
                        </Link>
                    );
                })}
            </motion.nav>
        </div>
    );
}

export default BottomNavBar;
