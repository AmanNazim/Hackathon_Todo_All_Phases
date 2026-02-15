const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { Pool } = require('pg');
require('dotenv').config();

async function testUpdatedConfig() {
  console.log('Testing updated Better Auth configuration with drizzle adapter...');

  if (!process.env.DATABASE_URL) {
    console.log('DATABASE_URL not set');
    return;
  }

  // Create a PostgreSQL pool for Neon compatibility
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false // Required for Neon
    }
  });

  try {
    const auth = betterAuth({
      adapter: drizzleAdapter(pool, { provider: 'pg' }), // Use drizzle adapter with PostgreSQL pool
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

    console.log('✓ Better Auth initialized successfully with drizzle adapter!');

    if (auth.db) {
      console.log('✓ Database adapter available with drizzle adapter!');

      try {
        const userCount = await auth.db.count('user');
        console.log('✓ Connected to database - user count:', userCount);
      } catch (dbErr) {
        console.log('⚠ Could not access database:', dbErr.message);
      }
    } else {
      console.log('✗ Database adapter not available');
    }

    // Close the pool
    await pool.end();
  } catch (error) {
    console.log('✗ Error with updated configuration:', error.message);
    console.log('Full error:', error);

    // Close the pool in case of error
    try {
      await pool.end();
    } catch (closeErr) {
      console.log('Error closing pool:', closeErr.message);
    }
  }
}

testUpdatedConfig().catch(console.error);