import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./styles/globals.css";

export const metadata: Metadata = {
  title: "Retail IQ",
  description: "Retail business intelligence and customer analytics platform",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
