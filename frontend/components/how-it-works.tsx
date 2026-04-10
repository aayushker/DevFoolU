"use client";

import { Upload, Zap, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";
import { TracingBeam } from "./ui/tracing-beam";

const steps = [
  {
    number: "01",
    title: "Paste Your Project URL",
    description:
      "Simply paste your Devfolio project URL. Our system securely fetches your project title, description, tech stack, and other metadata instantly.",
    icon: Upload,
    detail: "Works with any public Devfolio project link. No signup required for basic checks.",
    iconColor: "text-violet-400",
    bg: "from-violet-500/20 to-purple-500/10",
    border: "border-violet-500/30",
  },
  {
    number: "02",
    title: "AI Analyzes Everything",
    description:
      "Our transformer-based AI extracts semantic embeddings and cross-references your project against 1,136+ indexed hackathon projects in milliseconds.",
    icon: Zap,
    detail: "Semantic similarity, tech stack overlap, and description matching — all in one pass.",
    iconColor: "text-yellow-400",
    bg: "from-yellow-500/10 to-orange-500/5",
    border: "border-yellow-500/30",
  },
  {
    number: "03",
    title: "Receive Detailed Report",
    description:
      "Get a comprehensive similarity report with percentage scores, matched projects, and specific areas of concern — all in under 3 seconds.",
    icon: BarChart3,
    detail: "Export, share, or review the report directly in your browser.",
    iconColor: "text-green-400",
    bg: "from-green-500/10 to-emerald-500/5",
    border: "border-green-500/30",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="py-24 px-4 sm:px-6 lg:px-8 bg-[#050816] dark:bg-[#050816] relative overflow-hidden"
    >
      {/* Top divider */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />

      {/* Glow */}
      <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-violet-700/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-5xl mx-auto relative z-10">
        {/* Section header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="inline-block text-xs font-semibold tracking-widest uppercase text-purple-400 mb-4 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20"
          >
            How To Setup
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-extrabold text-white mb-4"
          >
            It takes less than a{" "}
            <span className="gradient-text">minute</span>
            <br />to check your project
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-gray-400 text-lg max-w-xl mx-auto"
          >
            See how you can check a project in seconds and get a full analysis report seamlessly.
          </motion.p>
        </div>

        {/* Tracing Beam + Steps */}
        <TracingBeam>
          <div className="space-y-12">
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.15 }}
                  viewport={{ once: true, margin: "-100px" }}
                  className="ml-8 md:ml-24"
                >
                  <div
                    className={`relative rounded-2xl border ${step.border} bg-gradient-to-br ${step.bg} bg-white/[0.03] p-6 group hover:border-purple-400/50 transition-all duration-300`}
                  >
                    <div className="flex flex-col md:flex-row md:items-start gap-6">
                      {/* Icon & number */}
                      <div className="flex md:flex-col items-center gap-3 md:gap-2 shrink-0">
                        <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                          <Icon size={24} className={step.iconColor} />
                        </div>
                        <span className="text-4xl font-black text-white/10 font-mono">{step.number}</span>
                      </div>
                      {/* Content */}
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                        <p className="text-gray-400 leading-relaxed mb-3">{step.description}</p>
                        <div className="flex items-start gap-2 text-sm">
                          <span className="text-purple-400 mt-0.5">→</span>
                          <span className="text-gray-500">{step.detail}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </TracingBeam>
      </div>
    </section>
  );
}
