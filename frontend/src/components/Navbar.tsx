"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: "/", label: "Dashboard", icon: "🏠" },
    { href: "/analysis/new", label: "New Analysis", icon: "📄" },
    { href: "/standards", label: "Standards Library", icon: "📚" },
  ];

  return (
    <nav className="bg-slate-900 border-b border-slate-700/50 sticky top-0 z-50 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/40 transition-shadow">
              म
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">
                Manak Mitra
              </h1>
              <p className="text-[10px] text-slate-400 -mt-1 tracking-wider uppercase">
                Standards Recommender
              </p>
            </div>
          </Link>

          {/* Navigation */}
          <div className="flex items-center gap-1">
            {links.map((link) => {
              const isActive = pathname === link.href || 
                (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-amber-500/15 text-amber-400 shadow-inner"
                      : "text-slate-300 hover:text-white hover:bg-slate-800"
                  }`}
                >
                  <span className="mr-1.5">{link.icon}</span>
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
