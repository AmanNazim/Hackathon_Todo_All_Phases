import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// Configure Neon for serverless compatibility and transaction behavior
// fetchConnectionCache improves connection caching performance in serverless environments
neonConfig.fetchConnectionCache = true;

// Lazy initialization - auth instance is created ONLY when getAuth() is called
let authInstance: ReturnType<typeof betterAuth> | null = null;

export async function getAuth() {
  console.log("🚀 [AUTH DEBUG] getAuth() function called");

  // Return cached instance if already initialized
  if (authInstance) {
    console.log("✅ [AUTH DEBUG] Returning cached auth instance");
    return authInstance;
  }

  console.log("🔍 [AUTH DEBUG] DATABASE_URL exists:", !!process.env.DATABASE_URL);
  console.log("🔍 [AUTH DEBUG] BETTER_AUTH_SECRET exists:", !!process.env.BETTER_AUTH_SECRET);
  console.log("🔍 [AUTH DEBUG] BETTER_AUTH_URL exists:", !!process.env.BETTER_AUTH_URL);
  console.log("🔍 [AUTH DEBUG] NEXT_PUBLIC_APP_URL exists:", !!process.env.NEXT_PUBLIC_APP_URL);

  // Initialize auth with database connection
  if (process.env.DATABASE_URL) {
    try {
      console.log("📡 [AUTH DEBUG] Creating Neon client with URL:", process.env.DATABASE_URL.replace(/\/\/[^:]+:([^@]+)@/, "//***:***@"));

      // Create Neon HTTP client - this handles connections for serverless
      const sql = neon(process.env.DATABASE_URL);
      console.log("✅ [AUTH DEBUG] Neon client created successfully");

      // Create drizzle instance - Better Auth manages its own internal schema
      const db = drizzle(sql);
      console.log("✅ [AUTH DEBUG] Drizzle instance created");

      console.log("📡 [AUTH DEBUG] Sending data to database URL, establishing connection...");

      // Initialize Better Auth with the drizzle adapter
      // The adapter needs the 'pg' provider to properly handle PostgreSQL-specific operations
      // and ensure transactions work as expected with Neon
      authInstance = betterAuth({
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
        databaseHooks: {
          user: {
            create: {
              before: async ({ data, ctx }) => {
                console.log("👤 [DB DEBUG] BEFORE USER CREATE - Attempting to create user:", data.email);
                return data;
              },
              after: async ({ data, ctx }) => {
                console.log("👤 [DB DEBUG] AFTER USER CREATE - User created successfully:", data.email);
                console.log("👤 [DB DEBUG] User ID:", data.id);
              }
            }
          }
        }
      });

      console.log("✅ [AUTH DEBUG] Better Auth initialized with drizzle adapter database connection");
    } catch (error) {
      console.error("❌ [AUTH DEBUG] Better Auth initialization error:", error);
      console.error("❌ [AUTH DEBUG] Error stack:", error.stack);
      throw error;
    }
  } else {
    console.error("❌ [AUTH DEBUG] DATABASE_URL not set! Auth will not work properly.");
    throw new Error("DATABASE_URL environment variable is required for Better Auth");
  }

  console.log("✅ [AUTH DEBUG] getAuth() completed successfully");
  return authInstance;
}
