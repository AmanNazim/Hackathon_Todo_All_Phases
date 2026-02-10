import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

// Lazy initialization - auth instance is created ONLY when getAuth() is called
let authInstance: ReturnType<typeof betterAuth> | null = null;

export function getAuth() {
  // Return cached instance if already initialized
  if (authInstance) {
    return authInstance;
  }

  // Initialize only at runtime (never during build)
  authInstance = betterAuth({
    database: process.env.DATABASE_URL ? {
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

  return authInstance;
}
