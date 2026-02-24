/**
 * Documentation: Neon HTTP Transaction Configuration for Better Auth
 *
 * The transaction persistence issue with Neon HTTP driver typically stems from:
 * 1. Caching behavior where writes aren't immediately committed
 * 2. HTTP driver response before transaction completion
 * 3. Configuration mismatch between adapter and DB instance
 *
 * Solutions implemented:
 * - Used neonConfig.fetchConnectionCache = true for optimal pooling
 * - Ensuring schema is properly bound in the drizzle instance
 * - Correct adapter configuration with appropriate provider
 */

import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import { baSchema } from './src/lib/ba-schema';

console.log("🚀 [CLI AUTH DEBUG] Initializing CLI auth configuration");
console.log("🔍 [CLI AUTH DEBUG] DATABASE_URL exists:", !!process.env.DATABASE_URL);
console.log("🔍 [CLI AUTH DEBUG] BETTER_AUTH_SECRET exists:", !!process.env.BETTER_AUTH_SECRET);

// Configure Neon for serverless compatibility to improve transaction handling
neonConfig.fetchConnectionCache = true;
console.log("⚙️ [CLI AUTH DEBUG] Neon configuration set");

// Use a function to create a fresh database instance when needed
// This helps ensure any transaction isolation issues are avoided
const createDbInstance = () => {
  console.log("📡 [CLI AUTH DEBUG] Creating database instance with URL:",
    process.env.DATABASE_URL ? process.env.DATABASE_URL.replace(/\/\/[^:]+:([^@]+)@/, "//***:***@") : "NOT SET");

  const sql = neon(process.env.DATABASE_URL!);
  console.log("✅ [CLI AUTH DEBUG] Neon client created");

  const dbInstance = drizzle(sql, { schema: baSchema });
  console.log("✅ [CLI AUTH DEBUG] Drizzle instance created with schema");

  return dbInstance;
};

// Create the database instance
const db = createDbInstance();
console.log("✅ [CLI AUTH DEBUG] Database instance created");

// Configure Better Auth with proper transaction handling for Neon
console.log("🔐 [CLI AUTH DEBUG] Initializing Better Auth with database connection...");
export const auth = betterAuth({
  // Use the drizzle adapter with the proper provider and database instance
  adapter: drizzleAdapter(db, {
    provider: "pg",  // Specify PostgreSQL provider
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: process.env.NODE_ENV === 'production', // Only required in production
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // 1 day
  },
  plugins: [],
  secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
  baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  trustedOrigins: [
    process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
  rateLimit: {
    enabled: process.env.NODE_ENV === 'production', // Only enable in production
    window: 60, // 1 minute window
    max: 100,
  },
  advanced: {
    useSecureCookies: true,
    defaultCookieAttributes: {
      sameSite: "lax",
    },
  },
});

console.log("✅ [CLI AUTH DEBUG] Better Auth CLI configuration completed");
export default auth;