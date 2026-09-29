"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type Language = "en" | "hi" | "gu" | "ta" | "mr" | "bn";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, section?: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGES: Record<string, string> = {
  en: "English",
  hi: "हिन्दी",
  gu: "ગુજરાતી",
  ta: "தமிழ்",
  mr: "मराठी",
  bn: "বাংলা",
};

import defaultTranslations from "../i18n/translations.json";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("en");
  const [translations, setTranslations] = useState<any>(defaultTranslations);


  const t = (key: string, section?: string) => {
    if (!translations[language]) return key;
    
    // Fallback to English if key missing in target language
    const currentLangDict = translations[language];
    const enDict = translations["en"];

    if (section) {
      if (currentLangDict[section] && currentLangDict[section][key]) {
        return currentLangDict[section][key];
      }
      if (enDict && enDict[section] && enDict[section][key]) {
        return enDict[section][key];
      }
      return key;
    }

    return currentLangDict[key] || (enDict && enDict[key]) || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center gap-2">
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as Language)}
        className="bg-transparent text-white border border-white/20 rounded-md px-2 py-1 text-sm focus:outline-none focus:border-white/40"
      >
        {Object.entries(LANGUAGES).map(([code, name]) => (
          <option key={code} value={code} className="text-slate-800">
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}
