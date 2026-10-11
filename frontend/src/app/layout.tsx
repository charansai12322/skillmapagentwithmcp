import type { Metadata } from "next";
import { DM_Sans, Inter } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SkillMap AI — Career Intelligence & Industry Signal Atlas",
  description:
    "Evidence-based AI industry research, skill demand mapping, and verified live job opportunities.",
  keywords: [
    "Career Intelligence",
    "Skill Demand",
    "AI Jobs",
    "Industry Analytics",
    "Tech Careers",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${dmSans.variable} ${inter.variable} h-full antialiased selection:bg-[#D7F36B] selection:text-[#111914]`}
    >
      <body className="min-h-full flex flex-col bg-[#F5F4EC] text-[#111914]">
        {children}
      </body>
    </html>
  );
}
