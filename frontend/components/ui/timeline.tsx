"use client";
import {
    useMotionValueEvent,
    useScroll,
    useTransform,
    motion,
} from "framer-motion";
import React, { useEffect, useRef, useState } from "react";

interface TimelineEntry {
    title: string;
    content: React.ReactNode;
}

export const Timeline = ({ data }: { data: TimelineEntry[] }) => {
    const ref = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [height, setHeight] = useState(0);

    useEffect(() => {
        if (ref.current) {
            const rect = ref.current.getBoundingClientRect();
            setHeight(rect.height);
        }
    }, [ref]);

    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start 10%", "end 50%"],
    });

    const heightTransform = useTransform(scrollYProgress, [0, 1], [0, height]);
    const opacityTransform = useTransform(scrollYProgress, [0, 0.1], [0, 1]);

    return (
        <div
            className="w-full bg-white dark:bg-neutral-950 font-sans md:px-10"
            ref={containerRef}
        >
            <div className="max-w-7xl mx-auto py-20 px-4 md:px-8 lg:px-10 flex flex-col items-center text-center">
                <h2 className="text-3xl md:text-6xl mb-6 text-black dark:text-white font-black tracking-tight">
                    System Features
                </h2>
                <p className="text-neutral-700 dark:text-neutral-300 text-base md:text-lg max-w-3xl">
                    A comprehensive walkthrough of our capabilities through the data pipeline.
                </p>
            </div>

            <div ref={ref} className="relative max-w-7xl mx-auto pb-20">
                {data.map((item, index) => (
                    <div
                        key={index}
                        className="flex justify-start pt-10 md:pt-40 md:gap-10"
                    >
                        <div className="sticky flex flex-col md:flex-row z-40 items-center top-40 self-start max-w-xs lg:max-w-sm md:w-full">
                            {/* Updated Glow Dot - Pure White */}
                            <div className="h-10 absolute left-3 md:left-3 w-10 rounded-full bg-black flex items-center justify-center border border-neutral-800 shadow-[0_0_20px_-5px_rgba(255,255,255,0.3)]">
                                <div className="h-3 w-3 rounded-full bg-white shadow-[0_0_15px_rgba(255,255,255,1)]" />
                            </div>

                            <h3 className="hidden md:block text-xl md:pl-20 md:text-5xl font-bold text-neutral-800 dark:text-neutral-200">
                                {item.title}
                            </h3>
                        </div>

                        <div className="relative pl-20 pr-4 md:pl-4 w-full">
                            <h3 className="md:hidden block text-2xl mb-4 text-left font-bold text-neutral-800 dark:text-neutral-200">
                                {item.title}
                            </h3>
                            {item.content}{" "}
                        </div>
                    </div>
                ))}
                <div
                    style={{
                        height: height + "px",
                    }}
                    className="absolute md:left-8 left-8 top-0 overflow-hidden w-[2px] bg-[linear-gradient(to_bottom,var(--tw-gradient-stops))] from-transparent from-[0%] via-neutral-200 dark:via-neutral-700 to-transparent to-[99%]  [mask-image:linear-gradient(to_bottom,transparent_0%,black_10%,black_90%,transparent_100%)] "
                >
                    <motion.div
                        style={{
                            height: heightTransform,
                            opacity: opacityTransform,
                        }}
                        className="absolute inset-x-0 top-0 w-[2px] bg-gradient-to-t from-white via-neutral-200 to-transparent from-[0%] via-[10%] rounded-full shadow-[0_0_15px_rgba(255,255,255,0.8)]"
                    />
                </div>
            </div>
        </div>
    );
};
