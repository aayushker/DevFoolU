"use client";
import { useMotionValue, motion, useMotionTemplate } from "framer-motion";
import { MouseEvent, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function CardSpotlight({
    children,
    radius = 350,
    color = "#7c3aed20",
    className,
    ...props
}: {
    radius?: number;
    color?: string;
    children: ReactNode;
    className?: string;
} & React.HTMLAttributes<HTMLDivElement>) {
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    function handleMouseMove({ currentTarget, clientX, clientY }: MouseEvent) {
        const { left, top } = currentTarget.getBoundingClientRect();
        mouseX.set(clientX - left);
        mouseY.set(clientY - top);
    }

    const background = useMotionTemplate`radial-gradient(${radius}px circle at ${mouseX}px ${mouseY}px, ${color}, transparent 80%)`;

    return (
        <div
            className={cn(
                "group relative rounded-xl border border-white/10 bg-white/5 p-6 cursor-pointer",
                className
            )}
            onMouseMove={handleMouseMove}
            {...props}
        >
            <motion.div
                className="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition duration-300 group-hover:opacity-100"
                style={{ background }}
            />
            {children}
        </div>
    );
}
