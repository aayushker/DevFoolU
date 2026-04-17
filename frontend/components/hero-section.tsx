"use client";

import Link from "next/link";
import { ArrowRight, Zap, Shield, Clock } from "lucide-react";
import { BackgroundBeams } from "./ui/background-beams";
import { FlipWords } from "./ui/flip-words";
import { motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.12, ease: "easeOut" as const },
  }),
};

export default function HeroSection() {
  const words = ["Confidence", "Seconds", "Precision", "Clarity"];

  const stats = [
    {
      icon: Zap,
      label: "Lightning Fast",
      value: "<3s",
      color: "text-yellow-400",
    },
    {
      icon: Shield,
      label: "99% Accurate",
      value: "AI Model",
      color: "text-green-400",
    },
    {
      icon: Clock,
      label: "Secure & Private",
      value: "End-to-End",
      color: "text-blue-400",
    },
  ];

  return (
    <section className="relative min-h-screen flex flex-col justify-center items-center pt-20 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden bg-[#050816] dark:bg-[#050816] light:bg-gray-50">
      {/* Purple orb background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[800px] h-[500px] rounded-full bg-gradient-to-b from-violet-600/40 via-purple-500/20 to-transparent blur-[100px]" />
        <div className="absolute top-[20%] left-[10%] w-[300px] h-[300px] rounded-full bg-purple-700/20 blur-[80px] animate-blob" />
        <div className="absolute top-[30%] right-[10%] w-[250px] h-[250px] rounded-full bg-violet-500/20 blur-[80px] animate-blob animation-delay-2000" />
      </div>

      {/* Aceternity Background Beams */}
      <BackgroundBeams className="opacity-60" />

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Spacer to preserve layout after removing badge */}
        <div className="mb-8 h-[34px]" aria-hidden="true" />

        {/* Headline */}
        <motion.h1
          custom={1}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="text-5xl md:text-7xl font-extrabold text-white mb-4 leading-tight tracking-tight"
        >
          Detect Project <span className="gradient-text">Plagiarism</span> with
        </motion.h1>

        {/* Flip words */}
        <motion.div
          custom={2}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="text-5xl md:text-7xl font-extrabold text-white mb-8 leading-tight min-h-[1.2em] flex justify-center items-center"
        >
          <FlipWords words={words} className="gradient-text" duration={2500} />
        </motion.div>

        {/* Subtext */}
        <motion.p
          custom={3}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed"
        >
          Ensure the originality of Devfolio projects with our advanced
          AI-powered plagiarism detection. Protect your intellectual work and
          build credibility before you submit.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          custom={4}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-20"
        >
          <Link
            href="/check"
            className="group relative inline-flex items-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white px-8 py-4 rounded-full font-semibold text-base hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            <span className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            <Zap size={18} className="relative z-10" />
            <span className="relative z-10">Check Your Project Now</span>
            <ArrowRight
              size={18}
              className="relative z-10 group-hover:translate-x-1 transition-transform"
            />
          </Link>
          <a
            href="#how-it-works"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-base border border-white/20 text-white/80 hover:border-purple-400/60 hover:text-white hover:bg-white/5 transition-all duration-300"
          >
            See How It Works
          </a>
        </motion.div>

        {/* Dashboard Preview Card */}
        <motion.div
          custom={5}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="relative mx-auto max-w-4xl"
        >
          <div className="relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md p-1 shadow-2xl shadow-black/50 animate-float">
            {/* Glow ring */}
            <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-r from-violet-600/40 via-purple-400/20 to-violet-600/40 blur-sm -z-10" />

            {/* Mock similarity report UI */}
            <div className="rounded-xl bg-[#0d0d1a] p-6 text-left">
              {/* Header row */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="ml-3 text-sm text-gray-400 font-mono">
                    DevFoolU — similarity report
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-purple-400 font-semibold bg-purple-500/20 px-3 py-1 rounded-full">
                    Analysis Complete
                  </span>
                </div>
              </div>

              {/* Project info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {[
                  {
                    label: "Project Analyzed",
                    value: "HackFlow 2024",
                    sub: "devfolio.co/projects/...",
                  },
                  {
                    label: "Similarity Score",
                    value: "12%",
                    sub: "Low Risk",
                    color: "text-green-400",
                  },
                  {
                    label: "Projects Checked",
                    value: "1,136",
                    sub: "in database",
                  },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="rounded-lg bg-white/5 border border-white/8 p-4"
                  >
                    <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                    <p
                      className={`text-lg font-bold ${item.color ?? "text-white"}`}
                    >
                      {item.value}
                    </p>
                    <p className="text-xs text-gray-500">{item.sub}</p>
                  </div>
                ))}
              </div>

              {/* Progress bars */}
              <div className="space-y-3">
                <p className="text-xs text-gray-500 mb-2 font-semibold uppercase tracking-wider">
                  Top Matches
                </p>
                {[
                  {
                    name: "AI-TaskBot",
                    score: 8,
                    color: "from-green-500 to-green-400",
                  },
                  {
                    name: "DevPilot v2",
                    score: 12,
                    color: "from-yellow-500 to-orange-400",
                  },
                  {
                    name: "HackSync Pro",
                    score: 6,
                    color: "from-green-500 to-emerald-400",
                  },
                ].map((match) => (
                  <div key={match.name} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-28 truncate">
                      {match.name}
                    </span>
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${match.color} rounded-full`}
                        style={{ width: `${match.score * 5}%` }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-white">
                      {match.score}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Stats row */}
        <motion.div
          custom={6}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="grid grid-cols-3 gap-4 mt-14 max-w-lg mx-auto"
        >
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div
                key={i}
                className="flex flex-col items-center gap-1 group cursor-default"
              >
                <Icon
                  size={20}
                  className={`${stat.color} mb-1 group-hover:scale-110 transition-transform`}
                />
                <p className="text-lg font-bold text-white">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.label}</p>
              </div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
