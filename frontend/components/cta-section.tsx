import Link from "next/link";
import { BackgroundBeams } from "./ui/background-beams";
import { ArrowRight, Zap } from "lucide-react";

export default function CTA() {
  return (
    <section className="relative py-32 px-4 sm:px-6 lg:px-8 bg-[#050816] overflow-hidden">
      {/* Top divider */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/40 to-transparent" />

      {/* Purple orb */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-violet-700/25 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[400px] h-[200px] bg-purple-600/20 rounded-full blur-[80px]" />
      </div>

      {/* Background beams */}
      <BackgroundBeams className="opacity-30" />

      <div className="relative z-10 max-w-3xl mx-auto text-center">
        <span className="inline-block text-xs font-semibold tracking-widest uppercase text-purple-400 mb-6 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20">
          Start Your Journey
        </span>

        <h2 className="text-4xl md:text-6xl font-extrabold text-white mb-6 leading-tight">
          Ready to dive in?{" "}
          <span className="gradient-text">Start your journey</span>{" "}
          today
        </h2>

        <p className="text-gray-400 text-lg mb-10 max-w-xl mx-auto">
          Verify your project originality, protect your work, and submit to hackathons with confidence.
          It&apos;s free to start.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/check"
            className="group inline-flex items-center gap-2 bg-gradient-to-r from-violet-600 to-purple-500 text-white px-8 py-4 rounded-full font-semibold text-base hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 relative overflow-hidden"
          >
            <span className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            <Zap size={18} className="relative z-10" />
            <span className="relative z-10">Get Started Free</span>
            <ArrowRight size={18} className="relative z-10 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        <p className="mt-6 text-sm text-gray-600">No signup required • Results in seconds • Free forever</p>
      </div>
    </section>
  );
}
