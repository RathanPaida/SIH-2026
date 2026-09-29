"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LanguageProvider, LanguageSwitcher, useLanguage } from "./LanguageContext";

function MainLayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { t } = useLanguage();

  const navItems = [
    { name: t("new_analysis", "nav"), path: "/analysis/new", icon: "➕" },
    { name: t("my_analyses", "nav"), path: "/dashboard", icon: "📊" },
    { name: t("standards_library", "nav"), path: "/standards", icon: "📚" },
    { name: t("evaluation", "nav") || "Evaluation", path: "/evaluation", icon: "📈" },
    { name: t("help", "nav"), path: "/help", icon: "❓" },
    { name: t("settings", "nav"), path: "/settings", icon: "⚙️" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Prototype Banner */}
      <div className="prototype-banner">
        {t("prototype_banner")}
      </div>

      {/* Top Bar */}
      <header className="topbar">
        <div className="flex items-center gap-4">
          <div className="font-bold text-xl flex items-center gap-2">
            <span className="text-saffron">मानक</span>
            <span className="text-white">Mitra</span>
          </div>
          <span className="text-xs px-2 py-0.5 bg-white/10 rounded-full border border-white/20">
            {t("app_subtitle")}
          </span>
        </div>
        <div className="flex items-center gap-6">
          <LanguageSwitcher />
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium">{t("procurement_officer")}</div>
              <div className="text-xs text-white/70">Gov Dept</div>
            </div>
            <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-bold border-2 border-white/20 shadow-sm">
              PO
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="sidebar shrink-0 py-4">
          <nav className="flex-1 px-2 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                href={item.path}
                className={`sidebar-link ${pathname.startsWith(item.path) || (item.path === '/analysis/new' && pathname.match(/^\/analysis\/\d+/)) ? 'active' : ''}`}
              >
                <span className="text-lg w-6 text-center">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </nav>
          
          <div className="px-4 mt-6">
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🇮🇳</div>
              <div className="text-sm font-semibold text-navy mb-1">
                {t("sidebar_card") || "Building Transparent and Compliant Procurement"}
              </div>
              <div className="text-xs text-slate-500">
                AI-Powered Recommendations for Indian Standards
              </div>
            </div>
          </div>
        </aside>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>

      {/* Footer Strip */}
      <footer className="footer-strip">
        {t("footer")}
      </footer>
    </div>
  );
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <MainLayoutContent>{children}</MainLayoutContent>
    </LanguageProvider>
  );
}
