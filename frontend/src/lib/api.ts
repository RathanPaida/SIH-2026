const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseJson(res: Response) {
  try {
    return await res.json();
  } catch (err) {
    const text = await res.clone().text().catch(() => "");
    throw new Error(`Failed to parse JSON response. Status: ${res.status}. Body: ${text.slice(0, 100)}`);
  }
}


// ──────────────────────────────────────────────
// Analyses (unified pipeline)
// ──────────────────────────────────────────────

export async function createAnalysis(file?: File, text?: string, options?: {
  domain_hint?: string;
  use_reranker?: boolean;
  include_allied?: boolean;
}) {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (text) formData.append("text", String(text));
  if (options?.domain_hint) formData.append("domain_hint", String(options.domain_hint));
  if (options?.use_reranker) formData.append("use_reranker", "true");
  if (options?.include_allied !== false) formData.append("include_allied", "true");

  const res = await fetch(`${API_BASE}/api/analyses`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || "Analysis failed");
  }
  return parseJson(res);
}

export async function listAnalyses() {
  const res = await fetch(`${API_BASE}/api/analyses`);
  if (!res.ok) throw new Error("Failed to fetch analyses");
  return parseJson(res);
}

export async function getAnalysis(id: number) {
  const res = await fetch(`${API_BASE}/api/analyses/${id}`);
  if (!res.ok) throw new Error("Failed to fetch analysis");
  return parseJson(res);
}

export async function getJobStatus(id: number) {
  const res = await fetch(`${API_BASE}/api/jobs/${id}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return parseJson(res);
}

export async function finalizeAnalysis(id: number) {
  const res = await fetch(`${API_BASE}/api/analyses/${id}/finalize`, { method: "POST" });
  if (!res.ok) throw new Error("Finalization failed");
  return parseJson(res);
}

export async function exportAnalysis(id: number, format: "pdf" | "docx" | "json" = "pdf") {
  const res = await fetch(`${API_BASE}/api/analyses/${id}/export?format=${format}`);
  if (!res.ok) throw new Error("Export failed");

  if (format === "json") return parseJson(res);

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `manak_mitra_${id}.${format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ──────────────────────────────────────────────
// Legacy endpoints (backward compat)
// ──────────────────────────────────────────────

export async function listTenders() {
  const res = await fetch(`${API_BASE}/api/tenders`);
  if (!res.ok) throw new Error("Failed to fetch tenders");
  return parseJson(res);
}

export async function getSampleTenders() {
  const res = await fetch(`${API_BASE}/api/sample-tenders`);
  if (!res.ok) throw new Error("Failed to fetch sample tenders");
  return parseJson(res);
}

export async function extractRequirements(file?: File, text?: string) {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (text) formData.append("text", text);
  const res = await fetch(`${API_BASE}/api/extract`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Extraction failed" }));
    throw new Error(err.detail || "Extraction failed");
  }
  return parseJson(res);
}

export async function getRecommendations(tenderId: number) {
  const res = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tender_id: tenderId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Recommendation failed" }));
    throw new Error(err.detail || "Recommendation failed");
  }
  return parseJson(res);
}

// ──────────────────────────────────────────────
// Review
// ──────────────────────────────────────────────

export async function getTenderReview(tenderId: number) {
  const res = await fetch(`${API_BASE}/api/tenders/${tenderId}/review`);
  if (!res.ok) throw new Error("Failed to fetch review");
  return parseJson(res);
}

export async function updateReviewDecision(
  recommendationId: number,
  decision: "approve" | "modify" | "reject" | "uncertain" | "accept" | "flag",
  comment?: string
) {
  // Map to backend enum
  const mapped = decision === "flag" ? "uncertain" : decision;

  const res = await fetch(`${API_BASE}/api/review/${recommendationId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision: mapped, officer_notes: comment }),
  });
  if (!res.ok) throw new Error("Failed to update review");
  return parseJson(res);
}

// ──────────────────────────────────────────────
// Standards
// ──────────────────────────────────────────────

export async function listStandards(search?: string, sector?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (sector) params.append("sector", sector);
  const res = await fetch(`${API_BASE}/api/standards?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch standards");
  return parseJson(res);
}

export async function listSectors() {
  const res = await fetch(`${API_BASE}/api/standards/sectors`);
  if (!res.ok) throw new Error("Failed to fetch sectors");
  return parseJson(res);
}

export async function getStandard(id: number) {
  const res = await fetch(`${API_BASE}/api/standards/${id}`);
  if (!res.ok) throw new Error("Failed to fetch standard");
  return parseJson(res);
}

// ──────────────────────────────────────────────
// Export (legacy)
// ──────────────────────────────────────────────

export async function exportReport(tenderId: number, format: "pdf" | "docx" = "pdf") {
  const res = await fetch(`${API_BASE}/api/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tender_id: tenderId, format }),
  });
  if (!res.ok) throw new Error("Export failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `manak_mitra_report_${tenderId}.${format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ──────────────────────────────────────────────
// Settings, Catalogue Sync, Evaluation
// ──────────────────────────────────────────────

export async function getSettings() {
  const res = await fetch(`${API_BASE}/api/settings`);
  if (!res.ok) throw new Error("Failed to fetch settings");
  return parseJson(res);
}

export async function updateSettings(settings: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error("Failed to update settings");
  return parseJson(res);
}

export async function syncCatalogue() {
  const res = await fetch(`${API_BASE}/api/catalogue/sync`, { method: "POST" });
  if (!res.ok) throw new Error("Sync failed");
  return parseJson(res);
}

export async function getEvaluationMetrics() {
  const res = await fetch(`${API_BASE}/api/metrics/evaluation`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return parseJson(res);
}

// ──────────────────────────────────────────────
// Health
// ──────────────────────────────────────────────

export async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}
