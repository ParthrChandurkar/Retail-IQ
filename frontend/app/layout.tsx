import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./styles/globals.css";
import { Providers } from "../components/providers/Providers";

export const metadata: Metadata = {
  title: "Retail IQ",
  description: "Retail business intelligence and customer analytics platform",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
