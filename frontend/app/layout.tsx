import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Riviera Beach RTCC-UIP',
  description: 'Riviera Beach Police Department - Real Time Crime Center Unified Intelligence Platform',
  icons: {
    icon: '/assets/rbpd/favicon.ico',
    shortcut: '/assets/rbpd/favicon.ico',
    apple: '/assets/rbpd/rbpd_logo_256.png',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  );
}
