const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { Pool } = require('pg');
const { drizzle } = require('drizzle-orm/node-postgres');
require('dotenv').config();

async function testDrizzleSetup() {
  console.log('Testing Drizzle setup with Better Auth...');

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
    // Create Drizzle instance
    const db = drizzle(pool);

    // Test direct Drizzle connection first
    try {
      // Test if we can connect and query
      const result = await db.execute('SELECT 1 as test');
      console.log('✓ Direct Drizzle connection successful!');
      console.log('  Test query result:', result[0]?.test || 'No result');
    } catch (drizzleErr) {
      console.log('✗ Direct Drizzle connection failed:', drizzleErr.message);
    }

    // Now try to use the drizzle adapter with Better Auth
    const auth = betterAuth({
      adapter: drizzleAdapter(db, { provider: 'pg' }), // Pass the Drizzle instance instead of pool
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

    console.log('✓ Better Auth initialized with Drizzle instance!');

    if (auth.db) {
      console.log('✓ Database adapter available!');

      try {
        const userCount = await auth.db.count('user');
        console.log('✓ Connected to database - user count:', userCount);
      } catch (dbErr) {
        console.log('⚠ Could not access user table:', dbErr.message);

        // Try to see if other tables exist
        try {
          // Try to list tables to see what's available
          const tablesResult = await db.execute(`
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
          `);
          console.log('Available tables:', tablesResult.rows.map(r => r.table_name));
        } catch (tableErr) {
          console.log('Could not list tables:', tableErr.message);
        }
      }
    } else {
      console.log('✗ Database adapter still not available');
    }

  } catch (error) {
    console.log('✗ Error with Drizzle setup:', error.message);
    console.log('Full error:', error);
  }

  // Close the pool
  await pool.end();
}

testDrizzleSetup().catch(console.error);