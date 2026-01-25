/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BETTER_AUTH_URL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
    ],
    domains: ['localhost', 'your-api-domain.com'],
  },
  // Performance optimizations
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: false,
  // Enable compression
  compress: true,
  // Optimize fonts and experimental features
  experimental: {
    typedRoutes: true,
    optimizePackageImports: ["react-icons", "lucide-react"],
  },
  // Webpack optimizations
  webpack: (config, { isServer, dev }) => {
    // Only optimize in production builds
    if (!dev && !isServer) {
      // Enable compression
      config.optimization.minimize = true;

      // Tree shaking optimizations
      config.optimization.usedExports = true;
      config.optimization.providedExports = true;
      config.optimization.sideEffects = true;
    }

    // Don't resolve fs module on client-side
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    return config;
  },
  // Additional performance settings
  poweredByHeader: false, // Reduce header size
  generateEtags: true, // Enable ETags for caching
  // Asset prefix can be used for CDN
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
};

module.exports = nextConfig;