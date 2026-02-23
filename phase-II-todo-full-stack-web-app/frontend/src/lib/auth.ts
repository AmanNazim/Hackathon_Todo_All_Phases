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
  // Return cached instance if already initialized
  if (authInstance) {
    return authInstance;
  }

  // Initialize auth with database connection
  if (process.env.DATABASE_URL) {
    try {
      // Create Neon HTTP client - this handles connections for serverless
      const sql = neon(process.env.DATABASE_URL);
      // Create drizzle instance - Better Auth manages its own internal schema
      const db = drizzle(sql);

      console.log("Better Auth: Creating drizzle adapter with database connection");

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
      });

      console.log("Better Auth initialized with drizzle adapter database connection");
    } catch (error) {
      console.error("Better Auth initialization error:", error);
      throw error;
    }
  } else {
    console.error("DATABASE_URL not set! Auth will not work properly.");
    throw new Error("DATABASE_URL environment variable is required for Better Auth");
  }

  return authInstance;
}
