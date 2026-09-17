/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/audio/:path*',
        destination: 'http://localhost:8000/audio/:path*',
      },
    ]
  },
}

module.exports = nextConfig
