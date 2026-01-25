"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
    const pathname = usePathname();

    const routes = [
        {
            href: "/dashboard",
            label: "Console",
            active: pathname === "/dashboard",
        },
        {
            href: "/sdk",
            label: "Sentinel SDK",
            active: pathname === "/sdk",
        },
        {
            href: "/oracle",
            label: "Oracle",
            active: pathname === "/oracle",
        },
        {
            href: "/ml-engine",
            label: "ML Engine",
            active: pathname === "/ml-engine",
        },
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
                <div className="mr-4 flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2 font-bold">
                        <span>Sentinel</span>
                    </Link>
                    <nav className="flex items-center space-x-6 text-sm font-medium">
                        {routes.map((route) => (
                            <Link
                                key={route.href}
                                href={route.href}
                                className={cn(
                                    "transition-colors hover:text-foreground/80",
                                    route.active ? "text-foreground" : "text-foreground/60"
                                )}
                            >
                                {route.label}
                            </Link>
                        ))}
                    </nav>
                </div>
                <div className="flex flex-1 items-center justify-end space-x-2">
                    <Button variant="outline" size="sm" asChild>
                        <Link href="https://github.com/sentinel-risk" target="_blank">
                            GitHub
                        </Link>
                    </Button>
                </div>
            </div>
        </header>
    );
}
