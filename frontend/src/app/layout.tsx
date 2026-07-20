import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { ToastProvider } from "@/components/ToastProvider";
import { QueryProvider } from "@/components/QueryProvider";

export const metadata: Metadata = {
  title: {
    default: "NeuroNet AI",
    template: "%s | NeuroNet AI",
  },
  description: "Multi-agent collaboration intelligence platform for analyzing team communications, decisions, and project health.",
  keywords: ["AI", "collaboration", "intelligence", "project management", "team analysis", "knowledge graph"],
  authors: [{ name: "NeuroNet AI" }],
  creator: "NeuroNet AI",
  publisher: "NeuroNet AI",
  metadataBase: new URL("https://neuronet.ai"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://neuronet.ai",
    title: "NeuroNet AI",
    description: "Multi-agent collaboration intelligence platform for analyzing team communications, decisions, and project health.",
    siteName: "NeuroNet AI",
    images: [
      {
        url: "/favicon.svg",
        width: 32,
        height: 32,
        alt: "NeuroNet AI Logo",
      },
    ],
  },
  twitter: {
    card: "summary",
    title: "NeuroNet AI",
    description: "Multi-agent collaboration intelligence platform for analyzing team communications, decisions, and project health.",
    creator: "@neuronet",
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
  manifest: "/manifest.json",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-body">
        <QueryProvider>
          <ToastProvider>
            <div className="flex min-h-screen">
              <Sidebar />
              <main className="flex-1 p-8">{children}</main>
            </div>
          </ToastProvider>
        </QueryProvider>
      </body>
    </html>
  );
}