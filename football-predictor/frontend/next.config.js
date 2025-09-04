/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003',
    NEXT_PUBLIC_APP_NAME: 'Football Predictor',
    NEXT_PUBLIC_APP_VERSION: '1.0.0'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'}/api/:path*`
      }
    ]
  },
  images: {
    domains: ['api.football-data.org', 'media.api-sports.io'],
    unoptimized: true
  }
}

module.exports = nextConfig