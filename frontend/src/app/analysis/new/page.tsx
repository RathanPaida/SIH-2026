"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import { createAnalysis, getSampleTenders } from "@/lib/api";
import { useLanguage } from "@/components/LanguageContext";

export default function NewAnalysisPage() {
  const router = useRouter();
  const { t } = useLanguage();
  
  const [mode, setMode] = useState<"upload" | "paste">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Advanced options
  const [domainHint, setDomainHint] = useState<string>("");
  const [useReranker, setUseReranker] = useState(false);
  const [includeAllied, setIncludeAllied] = useState(true);

  // Samples
  const [samples, setSamples] = useState<any[]>([]);
  const [showSamples, setShowSamples] = useState(false);

  const loadSamples = async () => {
    if (samples.length === 0) {
      try {
        const data = await getSampleTenders();
        setSamples(data);
      } catch (err) {
        console.error("Failed to load samples");
      }
    }
    setShowSamples(!showSamples);
  };

  const selectSample = (sampleText: string) => {
    setText(sampleText);
    setMode("paste");
    setShowSamples(false);
  };

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);

    try {
      const result = await createAnalysis(
        mode === "upload" ? file || undefined : undefined,
        mode === "paste" ? text : undefined,
        {
          domain_hint: domainHint || undefined,
          use_reranker: useReranker,
          include_allied: includeAllied,
        }
      );
      // Navigate to the analysis loading page
      router.push(`/analysis/${result.analysis_id}/loading`);
    } catch (err: any) {
      setError(err.message || "An error occurred");
      setLoading(false);
    }
  };

  const canSubmit = mode === "upload" ? !!file : text.trim().length > 50;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-navy mb-2">{t("new_analysis_title")}</h1>
        <p className="text-text-muted">
          {t("new_analysis_subtitle")}
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Main Input Area */}
        <div className="md:col-span-2 space-y-6">
          <div className="card p-1">
            <div className="flex bg-slate-50 rounded-[10px] p-1">
              <button
                onClick={() => setMode("upload")}
                className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all ${
                  mode === "upload" ? "bg-white shadow-sm text-primary" : "text-text-muted hover:text-text"
                }`}
              >
                {t("upload_tab")}
              </button>
              <button
                onClick={() => setMode("paste")}
                className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-all ${
                  mode === "paste" ? "bg-white shadow-sm text-primary" : "text-text-muted hover:text-text"
                }`}
              >
                {t("text_tab")}
              </button>
            </div>
          </div>

          <div className="card p-6 min-h-[300px]">
            {mode === "upload" ? (
              <div className="h-full flex flex-col">
                <FileUpload onFileSelect={setFile} />
              </div>
            ) : (
              <div className="h-full flex flex-col relative">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-navy">Tender Content</label>
                  <div className="relative">
                    <button
                      onClick={loadSamples}
                      className="text-sm text-primary hover:text-primary-dark font-medium"
                    >
                      {t("sample_menu")} ▾
                    </button>
                    {showSamples && (
                      <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-lg border border-slate-200 z-10 py-2">
                        {samples.length > 0 ? (
                          samples.map((s, i) => (
                            <button
                              key={i}
                              onClick={() => selectSample(s.text)}
                              className="w-full text-left px-4 py-2 hover:bg-slate-50 text-sm flex items-center gap-2"
                            >
                              <span>{s.icon}</span>
                              <span className="truncate">{s.title}</span>
                            </button>
                          ))
                        ) : (
                          <div className="px-4 py-2 text-sm text-slate-500">Loading...</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={t("textarea_placeholder")}
                  className="flex-1 w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-y min-h-[250px]"
                />
              </div>
            )}
          </div>
        </div>

        {/* Options Sidebar */}
        <div className="space-y-6">
          <div className="card p-5">
            <h3 className="font-semibold text-navy mb-4">Analysis Options</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Domain Hint (Optional)
                </label>
                <select
                  value={domainHint}
                  onChange={(e) => setDomainHint(e.target.value)}
                  className="w-full border border-slate-200 rounded-lg p-2 text-sm focus:outline-none focus:border-primary"
                >
                  <option value="">Auto-detect</option>
                  <option value="construction">Construction & Civil</option>
                  <option value="electrical">Electrical & Electronics</option>
                  <option value="it_hardware">IT & Hardware</option>
                  <option value="water_plumbing">Water & Plumbing</option>
                  <option value="safety">Safety Equipment</option>
                </select>
              </div>

              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex items-center mt-0.5">
                  <input
                    type="checkbox"
                    checked={includeAllied}
                    onChange={(e) => setIncludeAllied(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-slate-700 group-hover:text-primary transition-colors">Expand Allied Standards</div>
                  <div className="text-xs text-slate-500 mt-0.5">Include normative references & test methods from knowledge graph</div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex items-center mt-0.5">
                  <input
                    type="checkbox"
                    checked={useReranker}
                    onChange={(e) => setUseReranker(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-slate-700 group-hover:text-primary transition-colors">Cross-Encoder Re-ranking</div>
                  <div className="text-xs text-slate-500 mt-0.5">Higher precision matching (takes longer)</div>
                </div>
              </label>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100">
              {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!canSubmit || loading}
            className={`w-full py-3 px-4 rounded-xl text-white font-semibold transition-all shadow-sm
              ${canSubmit && !loading 
                ? 'bg-blue-600 hover:bg-blue-700 hover:shadow-md active:scale-[0.98]' 
                : 'bg-slate-300 cursor-not-allowed'
              }`}
          >
            {loading ? "Starting..." : (t("analyse_btn") || "Analyse")}
          </button>
        </div>
      </div>
    </div>
  );
}
