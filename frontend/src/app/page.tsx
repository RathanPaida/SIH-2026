"use client";

import Link from "next/link";
import { useLanguage } from "@/components/LanguageContext";

export default function Home() {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-[family-name:var(--font-inter)] selection:bg-saffron/30">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-navy text-white">
        {/* Background Gradients */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-navy to-indigo-950 opacity-90"></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-500/20 via-transparent to-transparent"></div>
        
        {/* Decorative Circles */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-saffron/10 rounded-full blur-3xl mix-blend-screen animate-pulse"></div>
        <div className="absolute bottom-10 right-20 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl mix-blend-screen"></div>

        <div className="relative max-w-7xl mx-auto px-6 pt-32 pb-40 flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 backdrop-blur-md mb-8">
            <span className="w-2 h-2 rounded-full bg-saffron animate-ping"></span>
            <span className="w-2 h-2 rounded-full bg-saffron absolute"></span>
            <span className="text-sm font-medium tracking-wide">SIH 2026 Prototype Ready</span>
          </div>

          <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight mb-6 drop-shadow-lg">
            <span className="text-saffron">मानक</span> Mitra
          </h1>
          
          <p className="text-xl md:text-3xl font-light text-blue-100 max-w-3xl mb-12 leading-relaxed">
            AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement.
          </p>

          <div className="flex flex-col sm:flex-row gap-6">
            <Link 
              href="/analysis/new"
              className="px-8 py-4 bg-saffron text-navy font-bold rounded-xl text-lg hover:bg-white hover:scale-105 transition-all duration-300 shadow-[0_0_40px_rgba(255,153,51,0.4)]"
            >
              Start New Analysis ✨
            </Link>
            <Link 
              href="/dashboard"
              className="px-8 py-4 bg-white/10 border border-white/20 text-white font-medium rounded-xl text-lg hover:bg-white/20 backdrop-blur-md transition-all duration-300"
            >
              View Dashboard &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative max-w-7xl mx-auto px-6 py-24 -mt-20">
        <div className="grid md:grid-cols-3 gap-8">
          
          {/* Card 1 */}
          <div className="bg-white/80 backdrop-blur-xl border border-slate-200 rounded-2xl p-8 shadow-xl hover:-translate-y-2 transition-transform duration-300">
            <div className="w-14 h-14 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center text-3xl mb-6 shadow-inner">
              ⚡
            </div>
            <h3 className="text-2xl font-bold text-slate-800 mb-3">12-Stage AI Pipeline</h3>
            <p className="text-slate-600 leading-relaxed">
              Instantly extracts atomic requirements, runs semantic search across the FAISS Vector Database, and verifies lifecycle statuses automatically.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white/80 backdrop-blur-xl border border-slate-200 rounded-2xl p-8 shadow-xl hover:-translate-y-2 transition-transform duration-300">
            <div className="w-14 h-14 bg-red-100 text-red-600 rounded-xl flex items-center justify-center text-3xl mb-6 shadow-inner">
              🛡️
            </div>
            <h3 className="text-2xl font-bold text-slate-800 mb-3">QCO Validation</h3>
            <p className="text-slate-600 leading-relaxed">
              Never miss a mandatory standard. The system instantly cross-references Quality Control Orders to flag items requiring compulsory ISI marking.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-white/80 backdrop-blur-xl border border-slate-200 rounded-2xl p-8 shadow-xl hover:-translate-y-2 transition-transform duration-300">
            <div className="w-14 h-14 bg-green-100 text-green-600 rounded-xl flex items-center justify-center text-3xl mb-6 shadow-inner">
              📊
            </div>
            <h3 className="text-2xl font-bold text-slate-800 mb-3">Coverage & Gap Analysis</h3>
            <p className="text-slate-600 leading-relaxed">
              Audits your entire tender against domain-specific checklists to detect missing requirements or conflicting, outdated specifications.
            </p>
          </div>

        </div>
      </div>
      
      <div className="flex-1"></div>

      <footer className="text-center py-8 text-slate-500 border-t border-slate-200 mt-12 bg-white">
        <p>Built for Smart India Hackathon (SIH 2026). Problem Statement: SIH26108</p>
      </footer>
    </div>
  );
}
