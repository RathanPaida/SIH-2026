"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getJobStatus } from "@/lib/api";

export default function AnalysisLoadingPage() {
  const { id } = useParams();
  const router = useRouter();
  const [job, setJob] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    let timer: NodeJS.Timeout;
    
    const poll = async () => {
      try {
        const data = await getJobStatus(Number(id));
        setJob(data);

        if (data.status === "completed") {
          setTimeout(() => {
            router.push(`/analysis/${id}`);
          }, 1000);
          return;
        }
        
        if (data.status === "failed") {
          setError(data.message || "Analysis failed");
          return;
        }

        // Continue polling
        timer = setTimeout(poll, 1500);
      } catch (err: any) {
        setError(err.message || "Failed to check status");
      }
    };

    poll();

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [id, router]);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20">
        <div className="card p-8 text-center border-red-200 bg-red-50">
          <div className="text-4xl mb-4">❌</div>
          <h2 className="text-xl font-bold text-red-800 mb-2">Analysis Failed</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/analysis/new")}
            className="px-6 py-2 bg-white text-red-700 font-medium rounded-lg border border-red-200 hover:bg-red-50 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const stages = job?.stages || [
    "Document processing",
    "Language detection",
    "Requirement extraction",
    "Standards retrieval",
    "Fusion & ranking",
    "Allied-standards expansion",
    "Lifecycle check",
    "QCO check",
    "Coverage-gap analysis",
    "Conflict detection",
    "Risk assessment",
    "Ready for review"
  ];
  
  const currentStageName = job?.stage || "Starting...";
  let currentIndex = stages.indexOf(currentStageName);
  if (currentIndex === -1) currentIndex = 0;
  if (job?.status === "completed") currentIndex = stages.length;

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 animate-fadeIn">
      <div className="card p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-50 mb-4">
            <span className="text-2xl animate-spin">⚙️</span>
          </div>
          <h2 className="text-xl font-bold text-navy mb-2">Analyzing Tender Specification</h2>
          <p className="text-text-muted text-sm">
            Please wait while our AI engine extracts requirements, retrieves standards, and performs compliance checks.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="h-2 bg-slate-100 rounded-full mb-8 overflow-hidden">
          <div 
            className="h-full bg-primary transition-all duration-500 ease-out" 
            style={{ width: `${job?.progress || 0}%` }}
          />
        </div>

        {/* Stepper */}
        <div className="space-y-1">
          {stages.map((stage: string, idx: number) => {
            const isDone = idx < currentIndex || job?.status === "completed";
            const isActive = idx === currentIndex && job?.status !== "completed";
            
            return (
              <div 
                key={stage} 
                className={`stepper-item ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
              >
                <div className={`stepper-dot ${isDone ? 'done' : isActive ? 'active' : 'pending'}`}>
                  {isDone ? '✓' : isActive ? '●' : ''}
                </div>
                <span>{stage}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
