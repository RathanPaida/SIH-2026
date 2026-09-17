const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ──────────────────────────────────────────────
// Tenders
// ──────────────────────────────────────────────

export async function listTenders() {
  const res = await fetch(`${API_BASE}/tenders`);
  if (!res.ok) throw new Error("Failed to fetch tenders");
  return res.json();
}

export async function getSampleTenders() {
  const res = await fetch(`${API_BASE}/sample-tenders`);
  if (!res.ok) throw new Error("Failed to fetch sample tenders");
  return res.json();
}

// ──────────────────────────────────────────────
// Extract
// ──────────────────────────────────────────────

export async function extractRequirements(file?: File, text?: string) {
  const formData = new FormData();
  if (file) {
    formData.append("file", file);
  }
  if (text) {
    formData.append("text", text);
  }

  const res = await fetch(`${API_BASE}/extract`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Extraction failed" }));
    throw new Error(err.detail || "Extraction failed");
  }
  return res.json();
}

// ──────────────────────────────────────────────
// Recommend
// ──────────────────────────────────────────────

export async function getRecommendations(tenderId: number) {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tender_id: tenderId }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Recommendation failed" }));
    throw new Error(err.detail || "Recommendation failed");
  }
  return res.json();
}

// ──────────────────────────────────────────────
// Review
// ──────────────────────────────────────────────

export async function getTenderReview(tenderId: number) {
  const res = await fetch(`${API_BASE}/tenders/${tenderId}/review`);
  if (!res.ok) throw new Error("Failed to fetch review");
  return res.json();
}

export async function updateReviewDecision(
  recommendationId: number,
  decision: "accept" | "reject" | "flag",
  officerNotes?: string
) {
  const res = await fetch(`${API_BASE}/review/${recommendationId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, officer_notes: officerNotes }),
  });

  if (!res.ok) throw new Error("Failed to update review");
  return res.json();
}

// ──────────────────────────────────────────────
// Standards
// ──────────────────────────────────────────────

export async function listStandards(search?: string, sector?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (sector) params.append("sector", sector);

  const res = await fetch(`${API_BASE}/standards?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch standards");
  return res.json();
}

export async function listSectors() {
  const res = await fetch(`${API_BASE}/standards/sectors`);
  if (!res.ok) throw new Error("Failed to fetch sectors");
  return res.json();
}

export async function getStandard(id: number) {
  const res = await fetch(`${API_BASE}/standards/${id}`);
  if (!res.ok) throw new Error("Failed to fetch standard");
  return res.json();
}

// ──────────────────────────────────────────────
// Export
// ──────────────────────────────────────────────

export async function exportReport(tenderId: number, format: "pdf" | "docx" = "pdf") {
  const res = await fetch(`${API_BASE}/export`, {
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
// Health
// ──────────────────────────────────────────────

export async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
