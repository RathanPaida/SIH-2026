import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/ClientLayout";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Manak Mitra — AI-Powered Indian Standards Recommender",
  description:
    "Identify applicable Indian Standards (IS) for procurement tender specifications using AI-powered analysis. Upload tender documents, extract requirements, and get ranked IS recommendations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full font-[family-name:var(--font-inter)]">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
