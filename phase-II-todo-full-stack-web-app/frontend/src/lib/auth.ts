import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

// Lazy initialization - auth instance is created ONLY when getAuth() is called
let authInstance: ReturnType<typeof betterAuth> | null = null;

export function getAuth() {
  // Return cached instance if already initialized
  if (authInstance) {
    return authInstance;
  }

  // CRITICAL: Skip database initialization during build time
  // We only skip during build phases, not at runtime
  const isBuildPhase =
    process.env.NEXT_PHASE === 'phase-production-build' ||
    process.env.NEXT_PHASE === 'phase-export';

  // Initialize auth (database only enabled during runtime, not build)
  if (!isBuildPhase && process.env.DATABASE_URL) {
    // Initialize Better Auth with direct database configuration
    authInstance = betterAuth({
      database: {
        provider: "postgresql", // Use direct PostgreSQL connection
        url: process.env.DATABASE_URL,
        autoMigrate: true, // Enable automatic table creation/migration
      },
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

    // For debugging: Log that initialization occurred
    console.log("Better Auth initialized with direct database connection");
  } else {
    // Initialize without database for build phases
    authInstance = betterAuth({
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

    // For debugging: Log that initialization occurred without DB
    console.log("Better Auth initialized without database (build phase)");
  }

  return authInstance;
}
