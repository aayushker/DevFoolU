"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { CardSpotlight } from "./ui/card-spotlight";

function useCountUp(target: number, duration = 2000, start = false) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime: number;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return count;
}

export default function StatsSection() {
  const [visible, setVisible] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => entry.isIntersecting && setVisible(true),
      { threshold: 0.2 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const projects = useCountUp(1136, 2000, visible);
  const analyzed = useCountUp(19, 1500, visible);

  const stats = [
    {
      label: "Indexed Projects",
      value: visible ? projects.toLocaleString() : "0",
      description: "Hackathon projects in our database",
      // icon: "📚",
      color: "#7c3aed",
    },
    {
      label: "Projects Analyzed",
      value: visible ? analyzed.toLocaleString() : "0",
      description: "Successfully processed & checked",
      // icon: "⚡",
      color: "#a855f7",
    },
    {
      label: "Average Check Time",
      value: "<3s",
      description: "From URL to full report",
      // icon: "⏱️",
      color: "#c084fc",
    },
  ];

  return (
    <section
      ref={sectionRef}
      className="py-24 px-4 sm:px-6 lg:px-8 bg-[#050816] dark:bg-[#050816] relative overflow-hidden"
    >
      {/* Section background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-violet-700/10 rounded-full blur-[80px]" />
      </div>

      {/* Horizontal divider line */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Trusted by row */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center text-sm font-medium text-gray-500 mb-12 tracking-widest uppercase"
        >
          Trusted by developers worldwide
        </motion.p>

        {/* Logo strip */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          viewport={{ once: true }}
          className="flex flex-wrap justify-center gap-8 mb-20 opacity-40"
        >
          {["Devfolio", "HackIndia", "HackMIT", "ETHIndia", "MLH"].map((name) => (
            <span key={name} className="text-lg font-semibold text-gray-400 tracking-wide">
              {name}
            </span>
          ))}
        </motion.div>

        {/* Stats grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              viewport={{ once: true }}
            >
              <CardSpotlight
                color={`${stat.color}30`}
                className="h-full flex flex-col items-center text-center p-8 bg-white/[0.03] border-white/10 rounded-2xl"
              >
               {/* <div className="text-4xl mb-4">{stat.icon}</div> */}
                <p className="text-5xl font-extrabold text-white mb-2 tabular-nums">
                  {stat.value}
                </p>
                <p className="text-lg font-semibold text-purple-300 mb-2">{stat.label}</p>
                <p className="text-sm text-gray-500">{stat.description}</p>
              </CardSpotlight>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
