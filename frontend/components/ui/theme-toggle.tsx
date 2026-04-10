"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => setMounted(true), []);

    if (!mounted) return null;

    const isDark = theme === "dark";

    return (
        <button
            onClick={() => setTheme(isDark ? "light" : "dark")}
            className={`relative w-9 h-9 flex items-center justify-center rounded-full border transition-all duration-300 hover:scale-110 ${isDark
                    ? "bg-white/10 hover:bg-white/20 border-white/20 text-white"
                    : "bg-gray-900/10 hover:bg-gray-900/20 border-gray-400/40 text-gray-700"
                }`}
            aria-label="Toggle theme"
        >
            {isDark ? (
                <Sun className="h-4 w-4 text-yellow-300" />
            ) : (
                <Moon className="h-4 w-4 text-gray-700" />
            )}
        </button>
    );
}
