import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Force clean build - updated 2026-02-10
  generateBuildId: async () => {
    return `build-${Date.now()}`;
  },

  // Optimize production builds
  reactStrictMode: true,

  // Ensure proper client-side rendering
  experimental: {
    optimizePackageImports: ['@/components', '@/lib'],
  },
};

export default nextConfig;
