/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed rewrites to prevent conflicts with frontend API routes
  // Frontend will use NEXT_PUBLIC_API_URL to call backend directly
  
  // Add webpack configuration for better development experience
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config
  },
}

module.exports = nextConfig 