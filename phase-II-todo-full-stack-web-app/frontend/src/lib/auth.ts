import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

// Skip database initialization during build time or when DATABASE_URL is not set
// This prevents "Failed to initialize database adapter" error during Vercel builds
const shouldInitializeDatabase =
  typeof window === 'undefined' && // Server-side only
  process.env.DATABASE_URL && // Database URL is set
  process.env.NODE_ENV !== 'test'; // Not in test environment

export const auth = betterAuth({
  database: shouldInitializeDatabase ? {
    provider: "postgres",
    url: process.env.DATABASE_URL,
  } : undefined,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  plugins: [nextCookies()],
  secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
});
