"use client";

import { useLanguage } from "@/components/LanguageContext";

export default function HelpPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-navy mb-2">{t("help") || "Help & Guide"}</h1>
        <p className="text-text-muted">Learn how to use Manak Mitra for procurement compliance.</p>
      </div>

      <div className="space-y-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">1. Starting a New Analysis</h2>
          <p className="text-sm text-slate-700 mb-4 leading-relaxed">
            Upload your procurement specification (Tender document) or paste the text directly. The AI engine will read the document, detect the language, and extract all technical, performance, and safety requirements.
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-700 space-y-2">
            <li><strong>Domain Hint:</strong> You can guide the AI by selecting a domain (e.g. Construction, Electrical).</li>
            <li><strong>Cross-Encoder:</strong> For higher accuracy, enable the reranker, though it takes slightly longer.</li>
            <li><strong>Allied Standards:</strong> Turn this on to include normative references from the knowledge graph.</li>
          </ul>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">2. Reviewing Results</h2>
          <p className="text-sm text-slate-700 mb-4 leading-relaxed">
            The Analysis Results page provides a unified workspace with the source document on the left and findings on the right.
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-700 space-y-3">
            <li><strong>Requirements Tab:</strong> Shows each extracted requirement alongside recommended standards. You can Approve, Reject, or Flag each one.</li>
            <li><strong>Coverage Tab:</strong> The Audit Engine detects if your specification is missing key requirements for its domain (e.g., missing fire safety in construction).</li>
            <li><strong>Conflicts Tab:</strong> Flags contradictions within the document or citations of outdated/superseded standards.</li>
            <li><strong>Audit Trail:</strong> A tamper-evident log of all AI actions and human decisions for accountability.</li>
          </ul>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">3. QCO & Lifecycle Checks</h2>
          <p className="text-sm text-slate-700 mb-2 leading-relaxed">
            Every recommended standard is verified against the BIS Knowledge Graph:
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-700 space-y-2">
            <li><span className="chip chip-red">QCO</span> Indicates the standard is under a Quality Control Order (mandatory ISI mark).</li>
            <li><span className="chip chip-amber">Outdated</span> Means the standard has a newer edition. The system will propose the correct replacement.</li>
          </ul>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">4. Export & Finalization</h2>
          <p className="text-sm text-slate-700 leading-relaxed">
            Once you have reviewed all recommendations, click "Finalize & Approve". You can then export the results as a clean PDF or DOCX report to append to your procurement file.
          </p>
        </div>
      </div>
    </div>
  );
}
