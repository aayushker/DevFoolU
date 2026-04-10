"use client";

import { useState } from "react";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { BackgroundBeams } from "@/components/ui/background-beams";
import { ArrowRight, Loader2, ExternalLink, Brain, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface SimilarProject {
  _id: string;
  urlOfProject: string;
  nameOfProject: string;
  descriptionOfProject: string;
  problemSolved: string;
  challengesFaced: string;
  technologiesUsed: string[];
  similarity_score: number;
}

interface AIVerdict {
  verdict: string;
  model: string;
  status: string;
  projects_analyzed: number;
}

interface SearchResponse {
  status: string;
  message: string;
  results: SimilarProject[];
  count: number;
  ai_verdict: AIVerdict;
}

function ScoreBar({ score }: { score: number }) {
  const pct = score * 100;
  const color = pct >= 70 ? "#ef4444" : pct >= 50 ? "#f59e0b" : "#22c55e";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-sm font-bold w-12 text-right" style={{ color }}>{pct.toFixed(1)}%</span>
    </div>
  );
}

export default function SimilarityPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8080/api/similarity/search-by-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error("Failed to search for similar projects");
      const data: SearchResponse = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "An error occurred while searching");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#050816]">
      <Navbar />
      <main className="flex-1 pt-24 pb-20 relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-violet-700/20 rounded-full blur-[120px] pointer-events-none" />
        <BackgroundBeams className="opacity-20" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Header */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-500 mb-5 shadow-lg shadow-purple-500/30">
              <Brain className="text-white" size={26} />
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-3">
              AI <span className="gradient-text">Similarity</span> Search
            </h1>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Find similar projects and get AI-powered insights with deep semantic analysis
            </p>
          </motion.div>

          {/* Search form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm p-6 mb-8"
          >
            <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://devfolio.co/projects/your-project"
                className="flex-1 px-4 py-3.5 bg-white/5 border border-white/15 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-600 text-sm transition-all"
              />
              <button
                type="submit"
                disabled={loading}
                className="flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white px-6 py-3.5 rounded-xl font-bold hover:shadow-lg hover:shadow-purple-500/40 transition-all disabled:opacity-60 text-sm whitespace-nowrap group"
              >
                {loading ? (
                  <><Loader2 size={18} className="animate-spin" /> Analyzing...</>
                ) : (
                  <>Search Similar <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" /></>
                )}
              </button>
            </form>

            {error && (
              <div className="mt-4 flex items-start gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
                <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </motion.div>

          {/* Results */}
          <AnimatePresence>
            {results && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Summary */}
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-white">{results.message}</h2>
                    <p className="text-sm text-gray-500 mt-0.5">
                      Status: <span className="text-green-400 font-semibold">{results.status}</span>
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-extrabold text-purple-400">{results.count}</div>
                    <div className="text-xs text-gray-500">Similar Projects</div>
                  </div>
                </div>

                {/* AI Verdict */}
                {results.ai_verdict && (
                  <div className="rounded-2xl border border-purple-500/30 bg-purple-500/5 overflow-hidden">
                    <div className="bg-gradient-to-r from-violet-600 to-purple-500 px-5 py-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Brain size={20} className="text-white" />
                        <div>
                          <h3 className="font-bold text-white text-sm">AI Analysis Summary</h3>
                          <p className="text-purple-200 text-xs">Using {results.ai_verdict.model}</p>
                        </div>
                      </div>
                      <span className="flex items-center gap-1.5 text-xs text-white bg-white/20 px-3 py-1 rounded-full font-semibold">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /> AI Active
                      </span>
                    </div>
                    <div className="p-5 space-y-3">
                      {results.ai_verdict.verdict.split("\n").map((line, idx) => {
                        const t = line.trim();
                        if (!t) return null;
                        if (t.startsWith("*") && t.includes("**")) {
                          const text = t.replace(/\*+/g, "").trim();
                          const [title, ...rest] = text.split(":");
                          const content = rest.join(":").trim();
                          return (
                            <div key={idx} className="rounded-xl border border-white/10 bg-white/[0.04] p-4">
                              <h4 className="text-white font-bold text-sm mb-1">{title.trim()} ✨</h4>
                              {content && <p className="text-gray-400 text-sm leading-relaxed">{content}</p>}
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  </div>
                )}

                {/* Project list */}
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
                  <h3 className="text-lg font-bold text-white mb-5">Similar Projects Details</h3>
                  <div className="space-y-4">
                    {results.results.map((proj, idx) => (
                      <div key={proj._id} className="rounded-xl border border-white/10 bg-white/[0.03] p-5 hover:border-purple-500/30 transition-all group">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xs font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded-full">
                                #{idx + 1}
                              </span>
                              <a
                                href={proj.urlOfProject} target="_blank" rel="noopener noreferrer"
                                className="text-white font-bold text-base hover:text-purple-300 transition-colors flex items-center gap-1.5 group/link"
                              >
                                {proj.nameOfProject}
                                <ExternalLink size={13} className="opacity-0 group-hover/link:opacity-100 transition-opacity" />
                              </a>
                            </div>
                            <p className="text-gray-500 text-sm mb-3 line-clamp-2">{proj.descriptionOfProject}</p>
                          </div>
                        </div>

                        <ScoreBar score={proj.similarity_score} />

                        {proj.technologiesUsed?.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-1.5">
                            {proj.technologiesUsed.map((t, i) => (
                              <span key={i} className="text-xs px-2 py-0.5 bg-white/5 border border-white/10 text-gray-500 rounded-md">
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
      <Footer />
    </div>
  );
}
