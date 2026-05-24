/**
 * =============================================================================
 * SMARTCAREER AI - Root Layout
 * =============================================================================
 */

import type { Metadata } from "next";
import { Inter, Fira_Code } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
  display: "swap",
});

const frontendBaseUrl =
  process.env.NEXT_PUBLIC_FRONTEND_URL?.trim() || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(frontendBaseUrl),
  title: {
    default: "IshTop - AI-Powered Career Platform",
    template: "%s | IshTop",
  },
  description:
    "Build stunning resumes with AI, find your dream job, and accelerate your career with IshTop.",
  keywords: [
    "AI resume builder",
    "job search",
    "career platform",
    "resume generator",
    "job matching",
    "career development",
  ],
  authors: [{ name: "IshTop Team" }],
  icons: {
    icon: [
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ishtop.uz",
    siteName: "IshTop",
    title: "IshTop - AI-Powered Career Platform",
    description: "Build stunning resumes with AI and find your dream job.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "IshTop",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "IshTop",
    description: "Build stunning resumes with AI and find your dream job.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${firaCode.variable}`}>
      <head>
        <meta name="theme-color" content="#06b6d4" />
      </head>
      <body className="min-h-screen scroll-smooth bg-background text-foreground font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}


