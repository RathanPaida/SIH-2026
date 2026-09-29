"use client";

import { useEffect, useState } from "react";
import { getSettings, updateSettings } from "@/lib/api";
import { useLanguage } from "@/components/LanguageContext";

export default function SettingsPage() {
  const { language, setLanguage, t } = useLanguage();
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getSettings()
      .then((data) => {
        setSettings(data);
        if (data.default_language && data.default_language !== language) {
           // just keep it in sync visually
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSettings(settings);
      alert("Settings saved successfully.");
    } catch {
      alert("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: string, value: any) => {
    setSettings((prev: any) => ({ ...prev, [key]: value }));
  };

  if (loading) return <div className="p-20 text-center">Loading settings...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fadeIn">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-navy mb-1">{t("settings")}</h1>
          <p className="text-text-muted">Configure application behavior and defaults.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-primary text-white font-medium rounded-lg hover:bg-primary-dark transition-colors shadow-sm disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      <div className="space-y-6">
        {/* General Settings */}
        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">General Preferences</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Default Language</label>
              <select
                value={settings?.default_language || "en"}
                onChange={(e) => {
                  handleChange("default_language", e.target.value);
                  setLanguage(e.target.value as any);
                }}
                className="w-full sm:w-1/2 bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-primary"
              >
                <option value="en">English</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="gu">Gujarati (ગુજરાતી)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="bn">Bengali (বাংলা)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Data Source</label>
              <select
                value={settings?.data_source || "sample"}
                onChange={(e) => handleChange("data_source", e.target.value)}
                className="w-full sm:w-1/2 bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-primary"
              >
                <option value="sample">Local Seed Data (Prototype)</option>
                <option value="bis_api" disabled>BIS Live API (Production - Coming Soon)</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Engine Settings */}
        <div className="card p-6">
          <h2 className="text-lg font-bold text-navy mb-4 border-b pb-2">AI Engine Configuration</h2>
          
          <div className="space-y-6">
            <div>
              <label className="flex items-center justify-between sm:w-1/2 mb-1">
                <span className="text-sm font-medium text-slate-700">Minimum Confidence Threshold</span>
                <span className="text-sm font-bold text-primary">{settings?.confidence_threshold}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={settings?.confidence_threshold || 55}
                onChange={(e) => handleChange("confidence_threshold", parseInt(e.target.value))}
                className="w-full sm:w-1/2 accent-primary"
              />
              <p className="text-xs text-slate-500 mt-1">Recommendations below this score will be filtered out.</p>
            </div>
            
            <label className="flex items-start gap-3 cursor-pointer group sm:w-1/2">
              <div className="relative flex items-center mt-0.5">
                <input
                  type="checkbox"
                  checked={settings?.use_reranker || false}
                  onChange={(e) => handleChange("use_reranker", e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-slate-700">Enable Cross-Encoder Reranking by Default</div>
                <div className="text-xs text-slate-500 mt-0.5">Improves precision but increases processing time.</div>
              </div>
            </label>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">LLM Provider</label>
              <select
                value={settings?.llm_provider || "mock"}
                onChange={(e) => handleChange("llm_provider", e.target.value)}
                className="w-full sm:w-1/2 bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:border-primary"
              >
                <option value="mock">Local Mock (Fastest for testing)</option>
                <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
                <option value="gemini">Google Gemini 1.5</option>
              </select>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
