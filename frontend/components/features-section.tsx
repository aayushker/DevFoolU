"use client";

import {
  Brain,
  Zap,
  Shield,
  Database,
  Code2,
  FileBarChart2,
} from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Detection",
    description:
      "State-of-the-art transformer models analyze your project's code, description, stack, and content semantics — not just text matching.",
    span: "md:col-span-2",
    iconColor: "text-violet-400",
    bg: "from-violet-500/10 to-purple-500/5",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Results in under 3 seconds with our optimized vector search pipeline.",
    span: "",
    iconColor: "text-yellow-400",
    bg: "from-yellow-500/10 to-orange-500/5",
  },
  {
    icon: Shield,
    title: "Bank-Level Security",
    description:
      "End-to-end encryption ensures your project data stays private and protected.",
    span: "",
    iconColor: "text-blue-400",
    bg: "from-blue-500/10 to-cyan-500/5",
  },
  {
    icon: Database,
    title: "1,136+ Indexed Projects",
    description:
      "One of the largest hackathon project databases for comprehensive coverage.",
    span: "",
    iconColor: "text-green-400",
    bg: "from-green-500/10 to-emerald-500/5",
  },
  {
    icon: Code2,
    title: "Tech Stack Analysis",
    description:
      "Understand technology-level similarities between projects beyond just content.",
    span: "md:col-span-2",
    iconColor: "text-pink-400",
    bg: "from-pink-500/10 to-rose-500/5",
  },
  {
    icon: FileBarChart2,
    title: "Clear, Actionable Reports",
    description:
      "Easy-to-understand similarity reports with matched project breakdowns.",
    span: "",
    iconColor: "text-cyan-400",
    bg: "from-cyan-500/10 to-sky-500/5",
  },
];

function FeatureCard({
  feature,
  index,
}: {
  feature: (typeof features)[0];
  index: number;
}) {
  const Icon = feature.icon;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      viewport={{ once: true, margin: "-50px" }}
      className={cn(
        "group relative rounded-2xl border border-white/10 bg-white/[0.03] p-6 hover:border-purple-500/40 hover:bg-white/[0.06] transition-all duration-300 cursor-default overflow-hidden",
        feature.span,
      )}
    >
      {/* Gradient bg on hover */}
      <div
        className={cn(
          "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-500",
          feature.bg,
        )}
      />
      {/* Shimmer border */}
      <div className="absolute inset-0 rounded-2xl border border-transparent group-hover:border-purple-500/30 transition-colors duration-300 pointer-events-none" />

      <div className="relative z-10">
        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
          <Icon size={22} className={feature.iconColor} />
        </div>
        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-purple-100 transition-colors">
          {feature.title}
        </h3>
        <p className="text-sm text-gray-400 leading-relaxed">
          {feature.description}
        </p>
      </div>
    </motion.div>
  );
}

export default function FeaturesSection() {
  return (
    <section
      id="features"
      className="py-24 px-4 sm:px-6 lg:px-8 bg-[#050816] dark:bg-[#050816] relative overflow-hidden"
    >
      {/* Divider */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />

      {/* Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-violet-800/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="inline-block text-xs font-semibold tracking-widest uppercase text-purple-400 mb-4 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20"
          >
            Features
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-extrabold text-white mb-4"
          >
            Power Features to <span className="gradient-text">Supercharge</span>
            <br />
            Your Detection
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-gray-400 text-lg max-w-2xl mx-auto"
          >
            DevFoolU is packed with smart, scalable capabilities designed to
            verify originality, boost confidence, and save time.
          </motion.p>
        </div>

        {/* Bento-style Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {features.map((feature, index) => (
            <FeatureCard key={index} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
