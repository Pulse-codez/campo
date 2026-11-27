import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Campus Support Companion",
  description: "Confidential peer-style support for university students in Kenya.",
  keywords: ["student support", "mental health", "campus", "Kenya", "counselling"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased min-h-screen flex flex-col">
        {children}
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#148967" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Campus Support" />
      </body>
    </html>
  );
}
