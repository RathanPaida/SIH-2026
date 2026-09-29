"use client";

import { useEffect, useState } from "react";
import { getEvaluationMetrics } from "@/lib/api";

export default function EvaluationPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvaluationMetrics()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-20 text-center">Loading metrics...</div>;
  }

  if (!data) {
    return <div className="p-20 text-center text-red-500">Failed to load metrics</div>;
  }

  const m = data.metrics;
  const rc = data.retrieval_comparison;
  const mm = data.manual_vs_manak_mitra;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-navy">Performance Evaluation</h1>
        <p className="text-text-muted">Metrics and benchmarks against the Gold Standard dataset.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* System Usage Stats */}
        <div className="card p-6">
          <h2 className="font-bold text-navy mb-4">System Usage</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-xs font-semibold mb-1">TOTAL ANALYSES</div>
              <div className="text-2xl font-bold text-slate-800">{m.total_analyses}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-xs font-semibold mb-1">RECOMMENDATIONS</div>
              <div className="text-2xl font-bold text-slate-800">{m.total_recommendations}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-xs font-semibold mb-1">OFFICER APPROVAL</div>
              <div className="text-2xl font-bold text-green">{m.officer_approval_rate}%</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-xs font-semibold mb-1">AVG. PROCESSING TIME</div>
              <div className="text-2xl font-bold text-primary">{m.avg_processing_time_ms} ms</div>
            </div>
          </div>
        </div>

        {/* Manual vs Manak Mitra */}
        <div className="card p-6 bg-white text-slate-800">
          <h2 className="font-bold mb-4 text-navy">Efficiency Impact (Manual vs Manak Mitra)</h2>
          <div className="flex flex-col gap-6">
            <div>
              <div className="text-slate-500 text-sm mb-1">Manual Processing (Avg)</div>
              <div className="text-3xl font-bold text-red-600">{mm.manual_avg_hours} Hours</div>
            </div>
            <div>
              <div className="text-slate-500 text-sm mb-1">Manak Mitra Pipeline</div>
              <div className="text-3xl font-bold text-green-600">{mm.manak_mitra_avg_seconds} Seconds</div>
            </div>
            <div className="mt-2 pt-4 border-t border-slate-100">
              <div className="text-amber-600 font-bold text-xl">{mm.time_saved_percent}% Time Saved</div>
            </div>
          </div>
        </div>
      </div>

      {/* Retrieval Benchmarks */}
      <div className="card p-6 mb-8">
        <h2 className="font-bold text-navy mb-4">Retrieval Benchmarks (Gold Set)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg">Strategy</th>
                <th className="px-4 py-3">Recall@5</th>
                <th className="px-4 py-3">Recall@10</th>
                <th className="px-4 py-3 rounded-tr-lg">Mean Reciprocal Rank (MRR)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="px-4 py-3 font-medium text-slate-700">Lexical (BM25)</td>
                <td className="px-4 py-3">{rc.lexical_only.recall_5}</td>
                <td className="px-4 py-3">{rc.lexical_only.recall_10}</td>
                <td className="px-4 py-3">{rc.lexical_only.mrr}</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium text-slate-700">Semantic (FAISS)</td>
                <td className="px-4 py-3">{rc.semantic_only.recall_5}</td>
                <td className="px-4 py-3">{rc.semantic_only.recall_10}</td>
                <td className="px-4 py-3">{rc.semantic_only.mrr}</td>
              </tr>
              <tr className="bg-blue-50/50">
                <td className="px-4 py-3 font-bold text-primary">Hybrid RRF (Lexical + Semantic)</td>
                <td className="px-4 py-3 font-bold text-primary">{rc.hybrid_rrf.recall_5}</td>
                <td className="px-4 py-3 font-bold text-primary">{rc.hybrid_rrf.recall_10}</td>
                <td className="px-4 py-3 font-bold text-primary">{rc.hybrid_rrf.mrr}</td>
              </tr>
              <tr className="bg-green/5">
                <td className="px-4 py-3 font-bold text-green">Hybrid + Graph + Reranker (Full Pipeline)</td>
                <td className="px-4 py-3 font-bold text-green">{rc.hybrid_reranker.recall_5}</td>
                <td className="px-4 py-3 font-bold text-green">{rc.hybrid_reranker.recall_10}</td>
                <td className="px-4 py-3 font-bold text-green">{rc.hybrid_reranker.mrr}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
