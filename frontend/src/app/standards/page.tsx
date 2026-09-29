"use client";

import { useEffect, useState } from "react";
import { listStandards, listSectors, syncCatalogue } from "@/lib/api";
import { useLanguage } from "@/components/LanguageContext";

export default function StandardsLibraryPage() {
  const { t } = useLanguage();
  const [standards, setStandards] = useState<any[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedSector, setSelectedSector] = useState("");
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [stds, secs] = await Promise.all([
          listStandards(),
          listSectors(),
        ]);
        setStandards(stds);
        setSectors(secs);
      } catch {
        console.error("Failed to load standards");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const results = await listStandards(search, selectedSector || undefined);
      setStandards(results);
    } catch {
      console.error("Search failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch();
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, selectedSector]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const result = await syncCatalogue();
      alert(`Sync Complete:\n- New Editions: ${result.new_editions}\n- Amendments: ${result.amendments}\n- QCO Updates: ${result.qco_updates}\n- Withdrawals: ${result.withdrawals}\n\nAffected Analyses: ${result.affected_analyses.length}`);
    } catch {
      alert("Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy mb-1">
            📚 {t("standards_library")}
          </h1>
          <p className="text-text-muted">
            Browse and search the Indian Standards knowledge base. {standards.length} records.
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 bg-blue-50 text-primary border border-blue-200 rounded-lg font-medium hover:bg-blue-100 transition-colors shadow-sm disabled:opacity-50"
        >
          {syncing ? "⏳ Syncing..." : "🔄 Sync with BIS Catalogue"}
        </button>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6 card p-3 bg-white border-slate-200">
        <div className="flex-1 relative">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by IS number, title, or keywords..."
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2.5 text-slate-800 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-inner"
          />
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
            🔍
          </span>
        </div>
        <select
          value={selectedSector}
          onChange={(e) => setSelectedSector(e.target.value)}
          className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary min-w-[180px] shadow-sm"
        >
          <option value="">All Sectors</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {/* Results */}
      {loading ? (
        <div className="text-center py-20 text-slate-500">Loading standards...</div>
      ) : standards.length === 0 ? (
        <div className="text-center py-12 card bg-slate-50 border-dashed border-2">
          <div className="text-4xl mb-3 opacity-40">🔍</div>
          <p className="text-slate-500 font-medium">No standards found matching your search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {standards.map((std) => (
            <div key={std.id} className="card p-4 hover:border-primary/30 transition-colors">
              <div className="flex justify-between items-start gap-4 mb-2">
                <span className="font-mono font-bold text-primary text-lg">{std.is_number}</span>
                <span className={`chip ${std.status === 'superseded' ? 'chip-amber' : 'chip-green'}`}>
                  {std.status === 'current' ? 'Active' : 'Superseded'}
                </span>
              </div>
              <h3 className="font-semibold text-slate-800 leading-snug mb-2">{std.title}</h3>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
                  {std.sector}
                </span>
                {std.qcos && std.qcos.length > 0 && (
                  <span className="text-xs bg-red-50 text-red-700 border border-red-100 px-2 py-1 rounded font-bold">
                    QCO
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-600 line-clamp-2" title={std.scope}>{std.scope}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
