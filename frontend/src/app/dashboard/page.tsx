"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listAnalyses } from "@/lib/api";

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await listAnalyses();
        setAnalyses(data);
      } catch (err: any) {
        console.error("Failed to load analyses:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fadeIn">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">My Analyses</h1>
          <p className="text-text-muted">Recent procurement specification compliance checks.</p>
        </div>
        <Link href="/analysis/new" className="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark transition-colors">
          + New Analysis
        </Link>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-500">Loading...</div>
      ) : analyses.length === 0 ? (
        <div className="card p-12 text-center bg-slate-50 border-dashed border-2">
          <div className="text-4xl mb-4">📄</div>
          <h3 className="text-lg font-bold text-navy mb-2">No Analyses Yet</h3>
          <p className="text-slate-500 mb-6">Upload your first procurement specification to get started.</p>
          <Link href="/analysis/new" className="px-6 py-2 bg-white border border-slate-300 rounded-lg font-medium hover:bg-slate-50 text-navy transition-colors">
            Create Analysis
          </Link>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
              <tr>
                <th className="px-6 py-4">Title / Domain</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Risk Level</th>
                <th className="px-6 py-4">Reqs / Standards</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analyses.map((a: any) => (
                <tr key={a.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-navy">{a.name || `Analysis #${a.id}`}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`chip ${
                      a.status === 'completed' ? 'chip-green' :
                      a.status === 'failed' ? 'chip-red' : 'chip-amber'
                    }`}>
                      {a.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {a.status === 'completed' ? (
                      <span className={`font-semibold ${
                        a.risk_level === 'High' ? 'text-status-red' :
                        a.risk_level === 'Medium' ? 'text-status-amber' : 'text-status-green'
                      }`}>
                        {a.risk_level} ({a.risk_score})
                      </span>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {a.status === 'completed' ? `${a.requirements_count} / ${a.standards_count}` : '-'}
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {new Date(a.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link 
                      href={a.status === 'completed' ? `/analysis/${a.id}` : `/analysis/${a.id}/loading`}
                      className="text-primary font-medium hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
