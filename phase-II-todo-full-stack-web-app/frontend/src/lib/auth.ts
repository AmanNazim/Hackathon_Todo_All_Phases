import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

// Lazy initialization - auth instance is created ONLY when getAuth() is called
let authInstance: ReturnType<typeof betterAuth> | null = null;

export async function getAuth() {
  // Return cached instance if already initialized
  if (authInstance) {
    return authInstance;
  }

  // Initialize auth with database connection
  // During serverless runtime, we always need the database connection
  if (process.env.DATABASE_URL) {
    try {
      // Configure Neon for serverless compatibility
      neonConfig.fetchConnectionCache = true;

      // Create Neon HTTP client
      const sql = neon(process.env.DATABASE_URL);
      const db = drizzle(sql);

      console.log("Better Auth: Creating drizzle adapter with database connection");

      // Initialize Better Auth with the drizzle adapter
      // Based on Better Auth best practices from skills
      authInstance = betterAuth({
        adapter: drizzleAdapter(db, {
          provider: "pg",
          // Let Better Auth use its internal schema - no explicit schema needed
        }), // Use drizzle adapter with Drizzle instance
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
        }
      });

      // For debugging: Log that initialization occurred
      console.log("Better Auth initialized with drizzle adapter database connection");
    } catch (error) {
      console.error("Better Auth initialization error:", error);
      throw error;
    }
  } else {
    // This case should only happen if DATABASE_URL is not set
    console.error("DATABASE_URL not set! Auth will not work properly.");
    throw new Error("DATABASE_URL environment variable is required for Better Auth");
  }

  return authInstance;
}
