"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Menu, X, Zap } from "lucide-react";
import AuthNav from "./AuthNav";
import { ThemeToggle } from "./ui/theme-toggle";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
  ];

  return (
    <nav
      className={`fixed w-full top-0 z-50 transition-all duration-500 ${scrolled
          ? "bg-black/80 backdrop-blur-xl border-b border-white/10 shadow-lg shadow-black/20"
          : "bg-transparent"
        }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div
          className={`flex justify-between items-center transition-all duration-300 ${scrolled ? "h-14" : "h-16"
            }`}
        >
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
            <div className="w-9 h-9 bg-gradient-to-br from-violet-600 to-purple-500 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/60 group-hover:scale-110 transition-all duration-300">
              <Zap className="text-white" size={18} />
            </div>
            <span className="font-bold text-lg text-white">
              Dev<span className="text-purple-400">Fool</span>You
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="relative px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors duration-200 group"
              >
                {link.label}
                <span className="absolute bottom-1 left-4 right-4 h-px bg-gradient-to-r from-purple-500 to-violet-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
              </Link>
            ))}
          </div>

          {/* Right side actions */}
          <div className="hidden md:flex items-center space-x-3">
            <ThemeToggle />
            <Link
              href="/check"
              className="relative inline-flex items-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white text-sm font-semibold px-5 py-2 rounded-full hover:shadow-lg hover:shadow-purple-500/40 transition-all duration-300 hover:scale-105 overflow-hidden group"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-purple-500 to-violet-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <Zap size={14} className="relative z-10" />
              <span className="relative z-10">Start Checking</span>
            </Link>
            <AuthNav />
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <ThemeToggle />
            <button
              className="w-9 h-9 flex items-center justify-center rounded-lg bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-colors"
              onClick={() => setIsOpen(!isOpen)}
              aria-label="Toggle menu"
            >
              {isOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 pt-2 space-y-1 border-t border-white/10 bg-black/90 backdrop-blur-xl rounded-b-2xl animate-in fade-in slide-in-from-top-2">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="block text-gray-300 hover:text-white hover:bg-white/10 py-2 px-4 rounded-lg transition-all duration-200"
                onClick={() => setIsOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/check"
              className="block bg-gradient-to-r from-violet-600 to-purple-500 text-white px-4 py-2 rounded-lg text-center font-semibold mx-2 transition-all hover:shadow-lg hover:shadow-purple-500/40"
              onClick={() => setIsOpen(false)}
            >
              Start Checking
            </Link>
            <div className="px-4 pt-1">
              <AuthNav />
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
