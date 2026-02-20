import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import { baSchema } from './src/lib/ba-schema';

// Configure Neon for serverless compatibility
neonConfig.fetchConnectionCache = true;

// Create Neon HTTP client and Drizzle instance
const sql = neon(process.env.DATABASE_URL!);
const db = drizzle(sql, { schema: baSchema });

// Export auth configuration for Better Auth CLI and MCP
export const auth = betterAuth({
  adapter: drizzleAdapter(db, { provider: "postgresql" }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  plugins: [],
  secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
  baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  trustedOrigins: [
    process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
  // Apply security best practices from Better Auth skills
  rateLimit: {
    enabled: true,
    window: 10,
    max: 100,
  },
  advanced: {
    useSecureCookies: true,
    defaultCookieAttributes: {
      sameSite: "lax",
    },
  },
});

export default auth;