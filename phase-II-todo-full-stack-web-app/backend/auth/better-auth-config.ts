import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next";

export const auth = betterAuth({
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
    nextCookies(),
  ],
  database: {
    // Configure your database connection here
    // For production, use a proper database (PostgreSQL, MySQL, etc.)
    // Example with Prisma:
    // provider: "prisma",
    // prisma: prismaClient,
  },
  /**
   * IMPORTANT: Configure a database to persist user data in production.
   * Without a database, user data will be stored in memory and lost on restart.
   */
});
