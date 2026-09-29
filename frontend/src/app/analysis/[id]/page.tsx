"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { getAnalysis, updateReviewDecision, exportAnalysis, finalizeAnalysis } from "@/lib/api";
import { useLanguage } from "@/components/LanguageContext";

export default function AnalysisResultsPage() {
  const params = useParams();
  const { t } = useLanguage();
  const analysisId = Number(params.id);

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("requirements");
  const [exporting, setExporting] = useState(false);
  const [finalizing, setFinalizing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const result = await getAnalysis(analysisId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDecision = async (recId: number, decision: "approve" | "modify" | "reject" | "uncertain") => {
    try {
      await updateReviewDecision(recId, decision);
      await loadData();
    } catch {
      console.error("Failed to update decision");
    }
  };

  const handleExport = async (format: "pdf" | "docx") => {
    setExporting(true);
    try {
      await exportAnalysis(analysisId, format);
    } catch {
      alert("Export failed");
    } finally {
      setExporting(false);
    }
  };

  const handleFinalize = async () => {
    setFinalizing(true);
    try {
      const res = await finalizeAnalysis(analysisId);
      if (!res.finalized) {
        alert(res.message);
      } else {
        await loadData();
        alert("Analysis finalized successfully.");
      }
    } catch {
      alert("Finalization failed");
    } finally {
      setFinalizing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-20">
        <div className="text-primary animate-spin text-4xl">⚙️</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center text-red-600">
        <h2 className="text-xl font-bold mb-2">Error Loading Analysis</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col animate-fadeIn">
      {/* Header Bar */}
      <div className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-xl font-bold text-navy">{data.name || `Analysis #${data.analysis_id}`}</h1>
          <div className="flex gap-4 mt-1 text-sm text-text-muted">
            {data.domain && <span className="capitalize">Domain: {data.domain.replace('_', ' ')}</span>}
            <span>Risk Level: <span className={`font-semibold ${data.risk_level === 'High' ? 'text-status-red' : data.risk_level === 'Medium' ? 'text-status-amber' : 'text-status-green'}`}>{data.risk_level}</span> ({data.risk_score}/100)</span>
            <span>{data.processing_time_ms ? `Analyzed in ${(data.processing_time_ms / 1000).toFixed(1)}s` : ''}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleExport("docx")}
            disabled={exporting}
            className="px-4 py-2 text-sm font-medium text-navy bg-slate-100 rounded-lg border border-slate-200 hover:bg-slate-200 transition-colors disabled:opacity-50"
          >
            📥 {t("export_docx")}
          </button>
          <button
            onClick={() => handleExport("pdf")}
            disabled={exporting}
            className="px-4 py-2 text-sm font-medium text-navy bg-slate-100 rounded-lg border border-slate-200 hover:bg-slate-200 transition-colors disabled:opacity-50"
          >
            📥 {t("export_pdf")}
          </button>
          <button
            onClick={handleFinalize}
            disabled={finalizing}
            className="px-5 py-2 text-sm font-medium text-white bg-green rounded-lg hover:bg-green/90 transition-colors shadow-sm disabled:opacity-50"
          >
            ✓ Finalize & Approve
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-slate-200 px-6 shrink-0">
        <div className="flex gap-6 -mb-px">
          {[
            { id: "requirements", label: t("requirements"), count: data.requirements_count },
            { id: "standards", label: t("standards"), count: data.standards_count },
            { id: "coverage", label: t("coverage"), count: data.gaps_count > 0 ? `⚠️ ${data.gaps_count}` : 0 },
            { id: "conflicts", label: t("conflicts"), count: data.conflicts_count > 0 ? `🔴 ${data.conflicts_count}` : 0 },
            { id: "audit", label: t("audit_trail") },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === tab.id 
                  ? "border-primary text-primary" 
                  : "border-transparent text-text-muted hover:text-navy hover:border-slate-300"
              }`}
            >
              {tab.label}
              {tab.count !== undefined && tab.count !== 0 && (
                <span className={`px-2 py-0.5 rounded-full text-xs ${activeTab === tab.id ? 'bg-primary/10' : 'bg-slate-100'}`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Two-Pane Workspace */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Pane: Document Viewer */}
        <div className="w-1/3 min-w-[300px] border-r border-slate-200 bg-white flex flex-col h-full overflow-hidden">
          <div className="p-3 border-b border-slate-100 bg-slate-50 text-xs font-semibold text-text-muted uppercase tracking-wider shrink-0">
            Source Document
          </div>
          <div className="flex-1 overflow-auto p-4 text-sm leading-relaxed text-slate-700 whitespace-pre-wrap font-serif">
            {data.raw_text}
          </div>
        </div>

        {/* Right Pane: Content based on active tab */}
        <div className="flex-1 overflow-auto bg-slate-50 p-6 h-full">
          {activeTab === "requirements" && (
            <div className="max-w-4xl space-y-6">
              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="card p-4">
                  <div className="text-slate-500 text-xs font-semibold mb-1">TOTAL REQS</div>
                  <div className="text-2xl font-bold text-navy">{data.requirements_count}</div>
                </div>
                <div className="card p-4">
                  <div className="text-slate-500 text-xs font-semibold mb-1">STANDARDS</div>
                  <div className="text-2xl font-bold text-primary">{data.standards_count}</div>
                </div>
                <div className="card p-4 bg-red-50 border-red-100">
                  <div className="text-red-600 text-xs font-semibold mb-1">QCO MANDATORY</div>
                  <div className="text-2xl font-bold text-red-700">{data.qco_mandatory_count}</div>
                </div>
                <div className="card p-4 bg-amber-50 border-amber-100">
                  <div className="text-amber-700 text-xs font-semibold mb-1">NEEDS REVIEW</div>
                  <div className="text-2xl font-bold text-amber-700">{data.needs_review_count}</div>
                </div>
              </div>

              {data.requirements.map((req: any, idx: number) => (
                <div key={req.requirement_id} className="card overflow-hidden">
                  <div className="p-4 border-b border-slate-100 bg-slate-50 flex gap-3">
                    <div className="w-6 h-6 rounded-md bg-white border border-slate-200 text-slate-500 text-xs flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                      {idx + 1}
                    </div>
                    <div>
                      <span className="chip chip-blue mb-2">{req.req_type}</span>
                      <p className="text-slate-800 font-medium leading-relaxed">{req.description}</p>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    {req.recommendations.length > 0 ? (
                      <div className="space-y-4">
                        {req.recommendations.map((rec: any) => (
                          <RecommendationCard key={rec.id} rec={rec} onDecision={handleDecision} t={t} />
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-6 text-slate-400 text-sm">
                        No standards found for this requirement.
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "coverage" && (
            <div className="max-w-4xl space-y-4">
              <h2 className="text-lg font-bold text-navy mb-4">Gap Detection Analysis</h2>
              {data.findings.filter((f: any) => f.kind === "gap").map((finding: any) => (
                <div key={finding.id} className="card p-5 border-l-4 border-l-status-amber">
                  <h3 className="font-bold text-slate-800 flex items-center gap-2">
                    <span className="text-status-amber">⚠️</span> {finding.title}
                  </h3>
                  <p className="text-sm text-slate-600 mt-2">{finding.description}</p>
                  {finding.proposed_fix && (
                    <div className="mt-3 p-3 bg-amber-50 text-amber-800 text-sm rounded-lg border border-amber-200/50">
                      <span className="font-semibold">Proposed Fix:</span> {finding.proposed_fix}
                    </div>
                  )}
                </div>
              ))}
              {data.findings.filter((f: any) => f.kind === "gap").length === 0 && (
                <div className="text-center py-10 text-slate-500">No coverage gaps detected.</div>
              )}
            </div>
          )}

          {activeTab === "conflicts" && (
            <div className="max-w-4xl space-y-4">
              <h2 className="text-lg font-bold text-navy mb-4">Conflicts & Risks Analysis</h2>
              {data.findings.filter((f: any) => f.kind === "conflict" || f.kind === "risk" || f.kind === "outdated").map((finding: any) => (
                <div key={finding.id} className={`card p-5 border-l-4 ${finding.severity === 'high' || finding.severity === 'critical' ? 'border-l-status-red' : 'border-l-status-amber'}`}>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-slate-800 flex items-center gap-2">
                      <span className={finding.severity === 'high' || finding.severity === 'critical' ? 'text-status-red' : 'text-status-amber'}>
                        {finding.severity === 'high' || finding.severity === 'critical' ? '🔴' : '⚠️'}
                      </span> 
                      {finding.title}
                    </h3>
                    <span className={`text-xs px-2 py-1 rounded font-bold uppercase ${finding.severity === 'high' || finding.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                      {finding.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">{finding.description}</p>
                  {finding.proposed_fix && (
                    <div className={`mt-3 p-3 text-sm rounded-lg border ${finding.severity === 'high' || finding.severity === 'critical' ? 'bg-red-50 text-red-800 border-red-200' : 'bg-amber-50 text-amber-800 border-amber-200'}`}>
                      <span className="font-semibold">Proposed Fix:</span> {finding.proposed_fix}
                    </div>
                  )}
                </div>
              ))}
              {data.findings.filter((f: any) => f.kind === "conflict" || f.kind === "risk" || f.kind === "outdated").length === 0 && (
                <div className="text-center py-10 text-slate-500">No conflicts or risks detected.</div>
              )}
            </div>
          )}

          {activeTab === "audit" && (
            <div className="max-w-4xl">
              <h2 className="text-lg font-bold text-navy mb-4">Audit Trail</h2>
              <div className="card overflow-hidden">
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
                    <tr>
                      <th className="px-6 py-3">Timestamp</th>
                      <th className="px-6 py-3">Actor</th>
                      <th className="px-6 py-3">Event</th>
                      <th className="px-6 py-3">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data.audit_log.map((log: any) => (
                      <tr key={log.id}>
                        <td className="px-6 py-3 text-slate-500 whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${log.actor === 'system' ? 'bg-slate-100 text-slate-600' : 'bg-blue-100 text-blue-700'}`}>
                            {log.actor}
                          </span>
                        </td>
                        <td className="px-6 py-3 font-medium text-slate-800">{log.event}</td>
                        <td className="px-6 py-3 text-slate-600">{log.detail}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          
          {activeTab === "standards" && (
            <div className="max-w-4xl space-y-4">
              <h2 className="text-lg font-bold text-navy mb-4">All Recommended Standards</h2>
              <div className="grid grid-cols-1 gap-4">
                 {/* Flatten all recommendations into a unique list of standards */}
                 {Array.from(new Map(data.requirements.flatMap((req:any) => req.recommendations).map((rec:any) => [rec.standard_id, rec])).values()).map((rec: any) => (
                    <div key={rec.id} className="card p-4">
                      <div className="flex gap-4">
                        <div className="font-mono font-bold text-primary">{rec.is_number}</div>
                        <div className="flex-1">
                          <div className="font-bold text-slate-800">{rec.title}</div>
                          {rec.verification?.qco?.qco_mandatory && (
                            <span className="chip chip-red mt-2">ISI Mark Mandatory</span>
                          )}
                        </div>
                      </div>
                    </div>
                 ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

function RecommendationCard({ rec, onDecision, t }: { rec: any, onDecision: any, t: any }) {
  const isApproved = rec.decision === "approve" || rec.decision === "accept";
  const isRejected = rec.decision === "reject";
  const isQCO = rec.verification?.qco?.qco_mandatory;
  const isOutdated = !rec.verification?.lifecycle?.edition_ok;

  return (
    <div className={`border rounded-xl transition-all ${isApproved ? 'border-green/40 bg-green/5' : isRejected ? 'border-red-300 bg-red-50 opacity-60' : 'border-slate-200 bg-white hover:border-primary/30'}`}>
      <div className="p-4">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="font-mono font-bold text-primary">{rec.is_number}</span>
              <span className={`chip ${rec.relationship_type === 'primary' ? 'chip-blue' : 'chip-gray'}`}>
                {rec.relationship_type}
              </span>
              {isQCO && <span className="chip chip-red">QCO</span>}
              {isOutdated ? (
                <span className="chip chip-amber">Outdated</span>
              ) : (
                <span className="chip chip-green">Verified</span>
              )}
            </div>
            <h4 className="font-semibold text-slate-800 text-sm leading-snug">{rec.title}</h4>
            
            {/* Confidence Bar */}
            <div className="mt-3 flex items-center gap-2 max-w-[200px]">
              <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden flex">
                <div 
                  className={`h-full ${rec.relevance_score > 0.7 ? 'bg-status-green' : rec.relevance_score > 0.4 ? 'bg-status-amber' : 'bg-slate-400'}`} 
                  style={{ width: `${Math.min(rec.relevance_score * 100, 100)}%` }}
                />
              </div>
              <span className="text-xs font-mono text-slate-500">{(rec.relevance_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          <div className="flex flex-col gap-2 shrink-0">
            <button 
              onClick={() => onDecision(rec.id, "approve")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-colors ${isApproved ? 'bg-green text-white border-green shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:bg-green/10 hover:text-green hover:border-green'}`}
            >
              ✓ Approve
            </button>
            <button 
              onClick={() => onDecision(rec.id, "reject")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-colors ${isRejected ? 'bg-red-600 text-white border-red-600 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200'}`}
            >
              ✕ Reject
            </button>
            <button 
              onClick={() => onDecision(rec.id, "uncertain")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-colors ${rec.decision === 'uncertain' ? 'bg-amber-500 text-white border-amber-500 shadow-sm' : 'bg-white text-slate-600 border-slate-200 hover:bg-amber-50 hover:text-amber-600 hover:border-amber-200'}`}
            >
              ⚠️ Flag
            </button>
          </div>
        </div>

        <div className="mt-3 bg-slate-50 p-3 rounded-lg border border-slate-100 text-sm text-slate-600 leading-relaxed">
          <span className="font-semibold text-slate-700">Justification: </span>
          {rec.justification}
        </div>
        
        {isOutdated && rec.correction && (
          <div className="mt-2 bg-amber-50 p-3 rounded-lg border border-amber-100 text-sm text-amber-800">
            <span className="font-semibold">Correction Required: </span>
            {rec.correction.message}. Suggest replacing with <span className="font-mono font-bold">{rec.correction.suggested_replacement}</span>.
          </div>
        )}
      </div>
    </div>
  );
}
