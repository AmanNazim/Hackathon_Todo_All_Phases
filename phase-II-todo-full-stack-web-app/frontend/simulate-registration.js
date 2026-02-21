/**
 * Script to simulate a real registration to trigger Better Auth table creation
 */
import dotenv from 'dotenv';
dotenv.config();

import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

async function simulateRegistration() {
  console.log('Simulating registration to trigger Better Auth table creation...');

  try {
    // Create database connection directly
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Initialize Better Auth with the drizzle adapter
    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg"
      }),
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
      },
      plugins: [],
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    console.log('Better Auth initialized, attempting to create a user...');

    // Create a mock request object for the registration
    const mockRequest = new Request('http://localhost:3000/api/auth/sign-up', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: `test-${Date.now()}@example.com`,
        password: 'TestPassword123!',
        name: 'Test User',
      }),
    });

    try {
      const result = await auth.api.signUpEmail({
        body: {
          email: `test-${Date.now()}@example.com`,
          password: 'TestPassword123!',
          name: 'Test User',
        },
        request: mockRequest,
      });

      console.log('Registration successful:', result?.user?.email);
    } catch (signUpError) {
      console.log('Registration attempt result:', signUpError.message);

      // Check if tables were created by querying
      try {
        const result = await db.execute('SELECT COUNT(*) FROM "user";');
        console.log('User table now exists and has', result.rows[0].count, 'users');
      } catch (countError) {
        console.log('User table still does not exist:', countError.message);
      }
    }

    console.log('Registration simulation completed');
  } catch (error) {
    console.error('Error in registration simulation:', error);
  }
}

// Run the simulation
simulateRegistration().catch(console.error);