import type { Metadata } from "next";
import { ThemeProvider } from "next-themes";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";
import { Auth0ProviderWithNavigate } from "@/lib/auth0-provider";
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "DevFoolU - Devfolio Project Plagiarism Checker",
  description:
    "Check your Devfolio projects for plagiarism and ensure originality before submission. AI-powered detection in seconds.",
  generator: "Next.js",
  keywords: [
    "plagiarism checker",
    "devfolio",
    "hackathon",
    "AI detection",
    "project originality",
  ],
  icons: {
    icon: [
      { url: "/icon-light-32x32.png", media: "(prefers-color-scheme: light)" },
      { url: "/icon-dark-32x32.png", media: "(prefers-color-scheme: dark)" },
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
    apple: "/apple-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange={false}
        >
          <Auth0ProviderWithNavigate>{children}</Auth0ProviderWithNavigate>
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  );
}
