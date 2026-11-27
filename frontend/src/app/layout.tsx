import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Campus Support Companion",
  description: "Confidential peer-style support for university students in Kenya.",
  keywords: ["student support", "mental health", "campus", "Kenya", "counselling"],
  manifest: "/manifest.json",
  appleWebApp: { capable: true, title: "Campus Support", statusBarStyle: "default" },
};

export const viewport: Viewport = {
  themeColor: "#1B4FD8",
};

// Runs before first paint so the saved theme never flashes. ?theme=light|dark overrides the saved choice.
const THEME_SCRIPT = `(function(){try{var q=new URLSearchParams(location.search).get('theme');var t=q||localStorage.getItem('csc_theme');if(t==='light'||t==='dark'){document.documentElement.dataset.theme=t;}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="antialiased min-h-screen flex flex-col">
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
        {children}
      </body>
    </html>
  );
}
