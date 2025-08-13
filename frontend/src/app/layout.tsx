import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Recaller - Privacy-First Personal Assistant",
  description: "Your privacy-first, open-source personal assistant app for managing finances, communications, social activities, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
