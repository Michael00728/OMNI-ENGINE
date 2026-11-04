import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OMNI-ENGINE | Credit Intelligence",
  description: "Evidence-based credit intelligence and financial optimization.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
