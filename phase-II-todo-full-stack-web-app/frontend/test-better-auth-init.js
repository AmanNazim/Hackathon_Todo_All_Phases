/**
 * Test script to initialize Better Auth and ensure tables are created
 */
import dotenv from 'dotenv';
dotenv.config();

// Import the actual auth.ts file (which needs to be compiled to JS) or use the compiled version
// Since auth.ts is a TypeScript file, we need to handle this differently
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
// Cannot directly import TypeScript files in Node.js without transpilation
// So we'll just create the auth instance without the explicit schema for now

async function testAuthInitialization() {
  console.log('Testing Better Auth initialization to create tables...');

  try {
    // Create database connection directly
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Initialize Better Auth with the drizzle adapter directly
    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg",
        // Let Better Auth use its own internal schema
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

    console.log('Better Auth instance created successfully');

    // Try to access the database adapter to trigger table creation
    if (auth.db) {
      console.log('Database adapter available');

      // Try to get user count (this should trigger table creation if needed)
      try {
        const result = await db.execute('SELECT COUNT(*) FROM "user";');
        console.log('User table exists and has', result.rows[0].count, 'users');
      } catch (countError) {
        console.log('User table may not exist yet (this may be expected):', countError.message);
        console.log('This is expected if tables have not been created yet.');
      }

      // Now try to trigger a real operation that should create tables if they don't exist
      try {
        console.log('Attempting to trigger table creation...');

        // Try to find a user (this operation should trigger table creation if needed)
        const userResult = await auth.api.get({
          url: '/api/auth/get-session',
          request: new Request('http://localhost:3000/api/auth/get-session', {
            headers: {
              'Content-Type': 'application/json'
            }
          })
        });

        console.log('Get session operation completed (tables should be created if they did not exist)');
      } catch (operationError) {
        console.log('Operation to trigger table creation (expected in some cases):', operationError.message);
      }
    }

    console.log('Better Auth initialization test completed');
  } catch (error) {
    console.error('Error in Better Auth initialization test:', error);
  }
}

// Run the test
testAuthInitialization().catch(console.error);