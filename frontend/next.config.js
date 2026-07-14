/**
 * Next.js Configuration
 * ============================================================================
 * Description: Configuration de Next.js pour le frontend GNL Knowledge Graph
 * ============================================================================
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Mode strict pour le développement
  reactStrictMode: true,
  
  // Swc minify pour de meilleures performances
  swcMinify: true,
  
  // Configuration des images
  images: {
    domains: ['localhost'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Récriture des routes vers l'API backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL 
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
      // ⚠️ Les rewrites ne supportent pas ws:// ou wss://
      // Nous supprimons donc la rewrite WebSocket
      // Le WebSocket sera géré directement par le client
    ];
  },
  
  // Headers de sécurité
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Variables d'environnement disponibles côté client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
    NEXT_PUBLIC_NEO4J_URL: process.env.NEXT_PUBLIC_NEO4J_URL || 'http://localhost:7474',
  },
  
  // Configuration du webpack
  webpack: (config, { isServer }) => {
    // Support des fichiers SVG en tant que composants React
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    
    // Support des fichiers graphql
    config.module.rules.push({
      test: /\.(graphql|gql)$/,
      exclude: /node_modules/,
      use: ['graphql-tag/loader'],
    });
    
    // Optimisation des bundles
    if (!isServer) {
      config.resolve.fallback = {
        fs: false,
        net: false,
        tls: false,
        crypto: false,
      };
    }
    
    return config;
  },
  
  // Experimental features
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  
  // Compression
  compress: true,
  
  // Production source maps
  productionBrowserSourceMaps: false,
};

module.exports = nextConfig;