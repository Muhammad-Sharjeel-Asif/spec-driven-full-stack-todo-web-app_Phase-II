import '@/styles/globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/providers/AuthProvider';
import PerformanceMonitor from '@/components/PerformanceMonitor';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Taskify - Task Management App',
  description: 'A simple and effective task management application',
  manifest: '/manifest.json',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=5',
  themeColor: '#6366f1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Preload critical resources */}
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
        <meta name="theme-color" content="#6366f1" />
        {/* Service Worker registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('ServiceWorker registration successful');
                    }, function(err) {
                      console.log('ServiceWorker registration failed');
                    });
                });
              }
            `,
          }}
        />
      </head>
      <body className={inter.className}>
        <PerformanceMonitor>
          <AuthProvider>
            {children}
          </AuthProvider>
        </PerformanceMonitor>
      </body>
    </html>
  );
}