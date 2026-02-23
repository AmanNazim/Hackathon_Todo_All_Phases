import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { Pool } from 'pg'; // Use traditional PostgreSQL client for stable transactions
import { drizzle } from 'drizzle-orm/node-postgres';

// Create PostgreSQL pool with Neon-compatible settings for backend
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false, // Required for Neon
  },
  // Connection pool settings for backend with Neon
  max: 10,  // Backend can handle more connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Create Drizzle instance with the PostgreSQL pool
const db = drizzle(pool);

export const auth = betterAuth({
  adapter: drizzleAdapter(db, {
    provider: "pg"
  }),
  emailAndPassword: {
    enabled: true,
    async sendResetPassword(data, request) {
      // Send an email to the user with a link to reset their password
      // This should be implemented with your email service (e.g., SendGrid, AWS SES)
      console.log('Password reset requested for:', data.user.email);
      console.log('Reset token:', data.token);
      // TODO: Implement email sending logic
    },
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  plugins: [
    // In backend context, don't use nextCookies - this is for frontend
  ],
  secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
  baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  trustedOrigins: [
    process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
});
