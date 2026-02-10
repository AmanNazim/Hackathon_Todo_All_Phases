import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

// Lazy initialization to prevent database connection during build time
let authInstance: ReturnType<typeof betterAuth> | null = null;

function getAuthInstance() {
  if (authInstance) {
    return authInstance;
  }

  // Only initialize with database in production runtime (not during build)
  const isProduction = process.env.NODE_ENV === 'production';
  const hasDatabaseUrl = !!process.env.DATABASE_URL;
  const isVercelBuild = process.env.VERCEL_ENV === undefined && isProduction;

  authInstance = betterAuth({
    database: hasDatabaseUrl && !isVercelBuild ? {
      provider: "postgres",
      url: process.env.DATABASE_URL!,
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

// Export a proxy that lazily initializes
export const auth = new Proxy({} as ReturnType<typeof betterAuth>, {
  get(target, prop) {
    const instance = getAuthInstance();
    return (instance as any)[prop];
  }
});
