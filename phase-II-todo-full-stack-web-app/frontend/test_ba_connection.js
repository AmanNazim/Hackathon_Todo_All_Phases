/**
 * Test script to verify Better Auth database connection and table creation
 */
require('dotenv').config();
const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { neon, neonConfig } = require('@neondatabase/serverless');
const { drizzle } = require('drizzle-orm/neon-http');

async function testBetterAuthConnection() {
  console.log('Testing Better Auth database connection and initialization...');

  if (!process.env.DATABASE_URL) {
    console.log('ERROR: DATABASE_URL environment variable not set');
    return;
  }

  try {
    // Configure Neon for serverless compatibility
    neonConfig.fetchConnectionCache = true;

    // Create Neon HTTP client
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('✓ Created Neon HTTP client and Drizzle instance');

    // Test direct database connection first
    try {
      const result = await sql`SELECT version();`;
      console.log('✓ Direct database connection successful');
      console.log('  Version:', result[0].version.substring(0, 50));
    } catch (dbErr) {
      console.log('✗ Direct database connection failed:', dbErr.message);
      return;
    }

    console.log('Initializing Better Auth with drizzle adapter...');

    // Initialize Better Auth with the drizzle adapter
    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg",
      }),
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
      },
      plugins: [require('better-auth/next-js').nextCookies()],
      secret: process.env.BETTER_AUTH_SECRET || 'dev-secret-change-in-production',
      baseURL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      ],
    });

    console.log('✓ Better Auth initialized successfully');

    // Check if the database adapter is available
    if (auth.db) {
      console.log('✓ Better Auth database adapter is available');

      // Try to query something to see if tables exist
      try {
        // Check if user table exists by attempting to count users
        const userResult = await sql`SELECT COUNT(*) as count FROM "user";`;
        console.log('✓ User table exists - found', userResult[0].count, 'users');
      } catch (countErr) {
        console.log('ℹ User table does not exist yet:', countErr.message);

        // This is expected after cleanup - tables should be created on first auth operation
        console.log('ℹ This is expected - tables should be created on first auth operation');
      }

      // Try to create a test user to trigger table creation
      console.log('Attempting to trigger table creation via registration...');
      try {
        const testEmail = `test_${Date.now()}@example.com`;
        const testPassword = 'TestPass123!';
        const testName = 'Test User';

        const result = await auth.api.signUpEmail({
          body: {
            email: testEmail,
            password: testPassword,
            name: testName,
          },
          headers: {
            'content-type': 'application/json',
          },
        });

        if (result?.session) {
          console.log('✓ Registration successful - tables should now be created');
          console.log('  - User ID:', result.session.userId);

          // Try to query the user table again
          try {
            const userResult = await sql`SELECT COUNT(*) as count FROM "user";`;
            console.log('✓ Verified user table exists with', userResult[0].count, 'users');
          } catch (verifyErr) {
            console.log('✗ Error verifying user table:', verifyErr.message);
          }
        } else {
          console.log('✗ Registration failed:', result?.error || 'Unknown error');
        }
      } catch (regErr) {
        console.log('✗ Error during registration attempt:', regErr.message);
        console.log('Stack:', regErr.stack);
      }
    } else {
      console.log('✗ Better Auth database adapter not available');
    }
  } catch (error) {
    console.log('✗ Error during Better Auth initialization:', error.message);
    console.log('Stack:', error.stack);
  }
}

testBetterAuthConnection().catch(console.error);