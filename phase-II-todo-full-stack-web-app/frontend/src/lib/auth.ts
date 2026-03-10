import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// Configure Neon for serverless compatibility and transaction behavior
// fetchConnectionCache improves connection caching performance in serverless environments
neonConfig.fetchConnectionCache = true;

export async function getAuth() {
  console.log("🚀 [AUTH DEBUG] getAuth() function called");
  console.log("🔄 [AUTH DEBUG] Creating FRESH auth instance (no caching for serverless compatibility)");

  console.log("🔍 [AUTH DEBUG] DATABASE_URL exists:", !!process.env.DATABASE_URL);
  console.log("🔍 [AUTH DEBUG] BETTER_AUTH_SECRET exists:", !!process.env.BETTER_AUTH_SECRET);
  console.log("🔍 [AUTH DEBUG] BETTER_AUTH_URL exists:", !!process.env.BETTER_AUTH_URL);
  console.log("🔍 [AUTH DEBUG] NEXT_PUBLIC_APP_URL exists:", !!process.env.NEXT_PUBLIC_APP_URL);

  // Initialize auth with database connection
  if (process.env.DATABASE_URL) {
    try {
      console.log("📡 [AUTH DEBUG] Creating Neon client with URL:", process.env.DATABASE_URL.replace(/\/\/[^:]+:([^@]+)@/, "//***:***@"));

      // Configure Neon for serverless compatibility
      neonConfig.fetchConnectionCache = true;

      // Create Neon HTTP client - this handles connections for serverless
      const sql = neon(process.env.DATABASE_URL);
      console.log("✅ [AUTH DEBUG] Neon client created successfully");

      // Create drizzle instance - Better Auth manages its own internal schema
      const db = drizzle(sql);
      console.log("✅ [AUTH DEBUG] Drizzle instance created");

      console.log("📡 [AUTH DEBUG] Initializing Better Auth with fresh database connection...");

      // Initialize Better Auth with the drizzle adapter (no caching for serverless)
      // The adapter needs the 'pg' provider to properly handle PostgreSQL-specific operations
      // and ensure transactions work as expected with Neon
      const freshAuthInstance = betterAuth({
        adapter: drizzleAdapter(db, {
          provider: "pg",
        }),
        emailAndPassword: {
          enabled: true,
          requireEmailVerification: false, // Disable email verification for development
        },
        session: {
          expiresIn: 60 * 60 * 24 * 7, // 7 days
          updateAge: 60 * 60 * 24, // 1 day
        },
        plugins: [nextCookies()],
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
          useSecureCookies: false, // Disable secure cookies in development to allow HTTP (not HTTPS)
          defaultCookieAttributes: {
            sameSite: "lax",
          },
        },
        // Add database hooks to track actual database operations
        databaseHooks: {
          user: {
            create: {
              before: async ({ data, context }) => {
                console.log("👤 [DB HOOK] BEFORE USER CREATE - About to create user:", data.email);
                return data;
              },
              after: async ({ data, context }) => {
                console.log("👤 [DB HOOK] AFTER USER CREATE - Successfully created user in database:", data.email);
                console.log("👤 [DB HOOK] Created user ID:", data.id);
              }
            }
          }
        }
      });

      console.log("✅ [AUTH DEBUG] Better Auth FRESH instance created with drizzle adapter database connection");
      return freshAuthInstance;
    } catch (error) {
      console.error("❌ [AUTH DEBUG] Better Auth initialization error:", (error as Error).message || error);
      console.error("❌ [AUTH DEBUG] Error stack:", (error as Error).stack);
      throw error;
    }
  } else {
    console.error("❌ [AUTH DEBUG] DATABASE_URL not set! Auth will not work properly.");
    throw new Error("DATABASE_URL environment variable is required for Better Auth");
  }
}
