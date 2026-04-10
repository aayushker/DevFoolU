"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { BackgroundBeams } from "@/components/ui/background-beams";
import { ArrowRight, Loader2, CheckCircle2, AlertCircle, Shield, Zap, Lock } from "lucide-react";
import { motion } from "framer-motion";

export default function CheckPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!url.trim()) {
      setError("Please enter a valid Devfolio project URL");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8080/api/similarity/search-by-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error("Failed to analyze project");

      const data = await response.json();
      setSuccess(true);
      sessionStorage.setItem("plagiarismResults", JSON.stringify(data));

      setTimeout(() => router.push("/results"), 1200);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred. Please try again.");
      setLoading(false);
    }
  };

  const whyCheck = [
    { icon: "✓", label: "Ensure project originality", color: "text-green-400" },
    { icon: "🛡️", label: "Protect your intellectual work", color: "text-blue-400" },
    { icon: "⚠️", label: "Avoid plagiarism concerns before submission", color: "text-yellow-400" },
    { icon: "⭐", label: "Build credibility and trust", color: "text-purple-400" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#050816] dark:bg-[#050816] light:bg-gray-50">
      <Navbar />
      <main className="flex-1 pt-24 pb-20 relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-violet-700/20 rounded-full blur-[120px]" />
        </div>
        <BackgroundBeams className="opacity-20" />

        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-500 mb-6 shadow-lg shadow-purple-500/30">
              <CheckCircle2 className="text-white" size={30} />
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-3">
              Check Your <span className="gradient-text">Project</span>
            </h1>
            <p className="text-gray-400 text-lg">
              Verify the originality of your Devfolio project in seconds
            </p>
          </motion.div>

          {/* Main form card */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm p-8 mb-8 group"
          >
            {/* Gradient border glow */}
            <div className="absolute -inset-[1px] rounded-2xl bg-gradient-to-r from-violet-600/30 via-purple-400/10 to-violet-600/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10 blur-sm" />

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Devfolio Project URL
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Paste the complete URL of your Devfolio project page
                </p>
                <div className="relative">
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://devfolio.co/projects/your-project-name"
                    className="w-full px-4 py-4 bg-white/5 border border-white/15 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-600 font-medium transition-all duration-200 hover:border-white/25"
                    disabled={loading || success}
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600">
                    {!loading && !success && <ArrowRight size={18} />}
                  </div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Format: <span className="text-gray-500">https://devfolio.co/projects/project-id</span>
                </p>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
                >
                  <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
                  <span className="text-sm font-medium">{error}</span>
                </motion.div>
              )}

              {success && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-3 px-4 py-3 rounded-xl bg-green-500/10 border border-green-500/30 text-green-400"
                >
                  <CheckCircle2 size={18} className="flex-shrink-0 mt-0.5 animate-pulse" />
                  <span className="text-sm font-medium">Analysis complete! Redirecting to results...</span>
                </motion.div>
              )}

              <button
                type="submit"
                disabled={loading || success}
                className="w-full relative overflow-hidden bg-gradient-to-r from-violet-600 to-purple-500 text-white py-4 rounded-xl font-bold hover:shadow-2xl hover:shadow-purple-500/40 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed hover:scale-[1.02] text-base group"
              >
                <span className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                {loading ? (
                  <>
                    <Loader2 className="animate-spin relative z-10" size={20} />
                    <span className="relative z-10">Analyzing Project...</span>
                  </>
                ) : success ? (
                  <>
                    <CheckCircle2 size={20} className="relative z-10" />
                    <span className="relative z-10">Redirecting...</span>
                  </>
                ) : (
                  <>
                    <span className="relative z-10">Check for Plagiarism</span>
                    <ArrowRight size={20} className="relative z-10 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
          </motion.div>

          {/* How it works mini section */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-8"
          >
            <h2 className="text-xl font-bold text-white mb-5 text-center">How It Works</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { step: "01", icon: "📤", title: "Submit URL", desc: "Enter your Devfolio project URL" },
                { step: "02", icon: "⚙️", title: "AI Analysis", desc: "We extract and process your project data" },
                { step: "03", icon: "📊", title: "Get Results", desc: "Receive a detailed similarity report" },
              ].map((item, i) => (
                <div
                  key={i}
                  className="group rounded-xl border border-white/10 bg-white/[0.03] p-5 hover:border-purple-500/40 hover:bg-white/[0.06] transition-all duration-300"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">{item.icon}</span>
                    <span className="text-xs font-mono text-purple-400 font-bold">{item.step}</span>
                  </div>
                  <h3 className="font-bold text-white mb-1">{item.title}</h3>
                  <p className="text-sm text-gray-500">{item.desc}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Why check section */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 mb-6"
          >
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Zap size={18} className="text-purple-400" />
              Why Check?
            </h2>
            <div className="grid md:grid-cols-2 gap-3">
              {whyCheck.map((item, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors">
                  <span className={`text-lg flex-shrink-0 ${item.color}`}>{item.icon}</span>
                  <span className="text-sm text-gray-400">{item.label}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Security notice */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex gap-3 items-start px-5 py-4 rounded-xl border border-purple-500/20 bg-purple-500/5"
          >
            <Lock size={18} className="text-purple-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-gray-400">
              <span className="font-semibold text-white">Your Privacy Matters: </span>
              Your project information is handled securely and only used for plagiarism detection.
            </p>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
