/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizeCss: true,
    optimizePackageImports: [
      'lucide-react',
      'date-fns',
      'lodash',
      'axios',
      'react-hook-form',
      'zustand'
    ]
  },
  // 启用压缩
  compress: true,
  // 启用图片优化
  images: {
    domains: ['localhost', 'your-domain.com'],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30天
  },
  // 启用增量构建和优化 - 简化配置
  webpack: (config, { dev, isServer }) => {
    // 移除有问题的配置，保留基本的优化
    // Next.js 14内置优化已足够强大，不需要过度自定义
    
    if (!dev && !isServer) {
      // 仅在生产环境启用优化
      config.optimization.minimize = true;
      config.optimization.usedExports = true;
      config.optimization.sideEffects = true;
    }

    return config;
  },
  // 启用缓存
  async headers() {
    return [
      {
        source: '/_next/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/images/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=86400, immutable',
          },
        ],
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate',
          },
        ],
      },
    ];
  },
  // 启用重定向
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },
}

module.exports = nextConfig
