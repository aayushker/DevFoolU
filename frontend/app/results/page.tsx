"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { ArrowLeft, ExternalLink, TrendingUp, Brain, AlertCircle } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface SimilarProject {
  _id: string;
  urlOfProject: string;
  nameOfProject: string;
  descriptionOfProject: string;
  technologiesUsed: string[];
  similarity_score: number;
}

interface AIVerdict {
  verdict: string;
  model: string;
  status: string;
  projects_analyzed: number;
}

interface ResultsData {
  status: string;
  message: string;
  results: SimilarProject[];
  count: number;
  ai_verdict?: AIVerdict;
}

function ScoreRing({ score }: { score: number }) {
  const pct = score * 100;
  const color = pct >= 70 ? "#ef4444" : pct >= 50 ? "#f59e0b" : "#22c55e";
  const label = pct >= 70 ? "High" : pct >= 50 ? "Moderate" : "Low";
  const r = 45;
  const circ = 2 * Math.PI * r;
  const dash = (circ * score).toFixed(1);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
          <circle
            cx="50" cy="50" r={r} fill="none"
            stroke={color} strokeWidth="8"
            strokeDasharray={`${dash} ${circ.toFixed(1)}`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-white">
          {pct.toFixed(0)}%
        </span>
      </div>
      <span className="text-xs font-semibold uppercase tracking-wider" style={{ color }}>{label}</span>
    </div>
  );
}

export default function ResultsPage() {
  const [results, setResults] = useState<ResultsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = sessionStorage.getItem("plagiarismResults");
    if (stored) setResults(JSON.parse(stored));
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#050816]">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/30 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 font-medium">Preparing your results...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen flex flex-col bg-[#050816]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center pt-24 pb-20">
          <div className="text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h1 className="text-3xl font-bold text-white mb-2">No Results Found</h1>
            <p className="text-gray-400 mb-6">Please check a project first</p>
            <Link
              href="/check"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white px-6 py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-500/40 transition-all"
            >
              Back to Check
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const avg = results.results.reduce((s, r) => s + r.similarity_score, 0) / results.results.length;
  const max = Math.max(...results.results.map((r) => r.similarity_score));

  const overallRisk = max >= 0.7 ? "High Risk" : max >= 0.5 ? "Moderate Risk" : "Low Risk";
  const riskColor = max >= 0.7 ? "text-red-400" : max >= 0.5 ? "text-yellow-400" : "text-green-400";
  const riskBg = max >= 0.7 ? "border-red-500/30 bg-red-500/10" : max >= 0.5 ? "border-yellow-500/30 bg-yellow-500/10" : "border-green-500/30 bg-green-500/10";

  return (
    <div className="min-h-screen flex flex-col bg-[#050816]">
      <Navbar />
      <main className="flex-1 pt-24 pb-20">
        {/* Top purple glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-violet-700/15 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Back link */}
          <Link
            href="/check"
            className="inline-flex items-center gap-2 text-gray-400 hover:text-purple-400 mb-8 transition-colors group"
          >
            <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
            Back to Check Another Project
          </Link>

          {/* Page header */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-2">
              Analysis <span className="gradient-text">Results</span>
            </h1>
            <p className="text-gray-400 text-lg">{results.message}</p>
          </motion.div>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid md:grid-cols-3 gap-4 mb-10"
          >
            {[
              { label: "Total Matches", value: results.results.length, icon: "📌" },
              { label: "Average Similarity", value: `${(avg * 100).toFixed(1)}%`, icon: "📊" },
              { label: "Highest Match", value: `${(max * 100).toFixed(1)}%`, icon: "⚠️" },
            ].map((s, i) => (
              <div key={i} className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 hover:border-purple-500/30 transition-all">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-1">{s.label}</p>
                    <p className="text-4xl font-extrabold text-white">{s.value}</p>
                  </div>
                  <span className="text-3xl">{s.icon}</span>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Overall verdict badge */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className={`flex items-center gap-3 px-5 py-4 rounded-xl border ${riskBg} mb-10`}
          >
            <AlertCircle size={20} className={riskColor} />
            <div>
              <span className={`font-bold ${riskColor}`}>{overallRisk}: </span>
              <span className="text-gray-400 text-sm">
                {max >= 0.7
                  ? "Significant similarity detected. Review matched projects carefully before submitting."
                  : max >= 0.5
                    ? "Moderate similarity found. Some overlap detected, review the matches below."
                    : "Low similarity detected. Your project appears to be largely original."}
              </span>
            </div>
          </motion.div>

          {/* AI Verdict */}
          {results.ai_verdict?.status === "success" && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="rounded-2xl border border-purple-500/30 bg-purple-500/5 mb-10 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-violet-600 to-purple-500 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Brain size={22} className="text-white" />
                  <div>
                    <h2 className="text-lg font-bold text-white">AI-Powered Analysis Summary</h2>
                    <p className="text-purple-200 text-xs">
                      Analyzed {results.ai_verdict.projects_analyzed} projects using {results.ai_verdict.model}
                    </p>
                  </div>
                </div>
                <span className="flex items-center gap-2 text-white text-xs font-semibold bg-white/20 px-3 py-1 rounded-full">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  AI Active
                </span>
              </div>
              <div className="p-6 space-y-4">
                {results.ai_verdict.verdict.split("\n").map((line, idx) => {
                  const trimmed = line.trim();
                  if (!trimmed) return null;
                  if (trimmed.startsWith("*") && trimmed.includes("**")) {
                    const text = trimmed.replace(/\*+/g, "").trim();
                    const [title, ...rest] = text.split(":");
                    const content = rest.join(":").trim();
                    return (
                      <div key={idx} className="rounded-xl border border-white/10 bg-white/[0.04] p-5">
                        <h3 className="text-white font-bold mb-2">{title.trim()} ✨</h3>
                        {content && <p className="text-gray-400 text-sm leading-relaxed">{content}</p>}
                      </div>
                    );
                  }
                  return null;
                })}

                {/* Tech tags */}
                {results.results.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Common Technologies Detected</p>
                    <div className="flex flex-wrap gap-2">
                      {Array.from(new Set(results.results.flatMap((p) => p.technologiesUsed || [])))
                        .slice(0, 20)
                        .map((tech, i) => (
                          <span key={i} className="px-3 py-1 text-xs font-semibold text-purple-300 bg-purple-500/10 border border-purple-500/30 rounded-full hover:border-purple-400/60 transition-colors cursor-default">
                            {tech}
                          </span>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Similar projects */}
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-white">Similar Projects Found</h2>
              <span className="px-3 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {results.results.length} result{results.results.length !== 1 ? "s" : ""}
              </span>
            </div>

            <div className="space-y-4">
              {results.results.map((project, index) => (
                <motion.div
                  key={project._id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.05 * index }}
                  className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 hover:border-purple-500/40 hover:bg-white/[0.06] transition-all duration-300"
                >
                  <div className="flex flex-col md:flex-row md:items-start gap-6">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xs font-bold text-gray-500 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
                          Match #{index + 1}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-200 transition-colors">
                        {project.nameOfProject}
                      </h3>
                      <p className="text-gray-400 text-sm leading-relaxed mb-4">{project.descriptionOfProject}</p>

                      {/* Technologies */}
                      <div className="mb-4">
                        <p className="text-xs font-bold text-gray-600 mb-2 uppercase tracking-wider">Technologies</p>
                        <div className="flex flex-wrap gap-2">
                          {project.technologiesUsed.map((tech, i) => (
                            <span key={i} className="text-xs px-2.5 py-1 bg-white/5 border border-white/10 text-gray-400 rounded-lg font-medium hover:border-purple-500/40 transition-colors">
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>

                      <a
                        href={project.urlOfProject}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-purple-400 hover:text-purple-300 font-semibold text-sm transition-colors group/link"
                      >
                        View Full Project
                        <ExternalLink size={14} className="group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                      </a>
                    </div>

                    <div className="flex-shrink-0">
                      <ScoreRing score={project.similarity_score} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Bottom actions */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Link
              href="/check"
              className="group flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white py-4 rounded-full font-bold hover:shadow-xl hover:shadow-purple-500/40 transition-all hover:scale-[1.02]"
            >
              <TrendingUp size={18} />
              Check Another Project
            </Link>
            <Link
              href="/"
              className="flex items-center justify-center gap-2 border border-white/15 text-gray-300 py-4 rounded-full font-bold hover:border-white/30 hover:text-white transition-all hover:scale-[1.02]"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
