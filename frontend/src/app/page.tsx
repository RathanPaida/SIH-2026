"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listTenders, healthCheck } from "@/lib/api";

interface TenderSummary {
  id: number;
  filename: string | null;
  title: string | null;
  created_at: string | null;
  requirement_count: number;
}

export default function Dashboard() {
  const [tenders, setTenders] = useState<TenderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const init = async () => {
      const online = await healthCheck();
      setBackendOnline(online);
      if (online) {
        try {
          const data = await listTenders();
          setTenders(data);
        } catch {
          console.error("Failed to load tenders");
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
          AI-Powered Standards Recommender
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 tracking-tight">
          Manak <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">Mitra</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
          Instantly identify applicable Indian Standards (IS) for your procurement tender specifications using AI-powered analysis.
        </p>
      </div>

      {/* Backend Status */}
      {backendOnline === false && (
        <div className="mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm text-center">
          ⚠️ Backend server is offline. Please start the FastAPI server at <code className="bg-slate-800 px-2 py-0.5 rounded text-xs">http://localhost:8000</code>
        </div>
      )}

      {/* Action Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Link
          href="/analysis/new"
          className="group relative bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700/50 rounded-2xl p-6 hover:border-amber-500/40 transition-all duration-300 hover:shadow-xl hover:shadow-amber-500/5 hover:-translate-y-0.5"
        >
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-2xl mb-4 shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/40 transition-shadow">
            📄
          </div>
          <h3 className="text-white font-semibold text-lg mb-2">New Analysis</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Upload a tender document or paste text to extract requirements and get IS recommendations.
          </p>
          <div className="mt-4 text-amber-400 text-sm font-medium group-hover:translate-x-1 transition-transform">
            Get started →
          </div>
        </Link>

        <Link
          href="/standards"
          className="group relative bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700/50 rounded-2xl p-6 hover:border-blue-500/40 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5 hover:-translate-y-0.5"
        >
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-2xl mb-4 shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
            📚
          </div>
          <h3 className="text-white font-semibold text-lg mb-2">Standards Library</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Browse and search the Indian Standards knowledge base across all sectors.
          </p>
          <div className="mt-4 text-blue-400 text-sm font-medium group-hover:translate-x-1 transition-transform">
            Browse library →
          </div>
        </Link>

        <div className="relative bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700/30 rounded-2xl p-6 opacity-60">
          <div className="absolute top-4 right-4 text-[10px] bg-slate-700/50 text-slate-400 px-2 py-0.5 rounded-full">
            Coming Soon
          </div>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/50 to-teal-500/50 flex items-center justify-center text-2xl mb-4">
            🌐
          </div>
          <h3 className="text-slate-300 font-semibold text-lg mb-2">Live BIS Integration</h3>
          <p className="text-slate-500 text-sm leading-relaxed">
            Real-time lookup against BIS catalog, GeM marketplace, and CPPP portal.
          </p>
        </div>
      </div>

      {/* Recent Analyses */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <span>📋</span> Recent Analyses
        </h2>

        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading...</div>
        ) : tenders.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/30 border border-slate-700/30 rounded-2xl">
            <div className="text-4xl mb-3 opacity-40">📭</div>
            <p className="text-slate-400 mb-2">No analyses yet</p>
            <p className="text-slate-500 text-sm">
              Upload your first tender document to get started.
            </p>
          </div>
        ) : (
          <div className="bg-slate-800/30 border border-slate-700/30 rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider px-6 py-3">
                    Tender
                  </th>
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider px-6 py-3">
                    File
                  </th>
                  <th className="text-center text-xs font-medium text-slate-400 uppercase tracking-wider px-6 py-3">
                    Requirements
                  </th>
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider px-6 py-3">
                    Date
                  </th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/30">
                {tenders.map((tender) => (
                  <tr
                    key={tender.id}
                    className="hover:bg-slate-700/20 transition-colors"
                  >
                    <td className="px-6 py-4 text-white text-sm font-medium">
                      {tender.title || `Tender #${tender.id}`}
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-sm">
                      {tender.filename || "—"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="inline-flex items-center justify-center min-w-[28px] h-7 px-2 rounded-full bg-amber-500/15 text-amber-400 text-xs font-medium">
                        {tender.requirement_count}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-sm">
                      {tender.created_at
                        ? new Date(tender.created_at).toLocaleDateString("en-IN", {
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          })
                        : "—"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/analysis/${tender.id}`}
                        className="text-amber-400 hover:text-amber-300 text-sm font-medium transition-colors"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
