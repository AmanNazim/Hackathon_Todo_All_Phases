const { betterAuth } = require("better-auth");

// Load environment variables
require('dotenv').config();

async function testBetterAuthConnection() {
  console.log('Testing Better Auth database connection...');
  console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'SET' : 'NOT SET');
  console.log('BETTER_AUTH_SECRET:', process.env.BETTER_AUTH_SECRET ? 'SET' : 'NOT SET');

  try {
    // Initialize Better Auth with database configuration similar to your frontend
    const auth = betterAuth({
      database: process.env.DATABASE_URL ? {
        provider: "postgres",
        url: process.env.DATABASE_URL,
        autoMigrate: true, // Enable automatic table creation/migration
      } : undefined,
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
      },
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    console.log('Better Auth initialized successfully!');

    // Try to access the database adapter to see if connection works
    if (auth.db) {
      console.log('Database adapter available');

      // Try to ping the database
      try {
        const userCount = await auth.db.count('user'); // Try to count users table
        console.log('Database connection successful - users table accessible. Count:', userCount);
      } catch (dbErr) {
        console.log('Database connection failed or users table does not exist:', dbErr.message);
      }
    } else {
      console.log('Database adapter not available - check DATABASE_URL');
    }

  } catch (error) {
    console.error('Error initializing Better Auth:', error.message);
    console.error('Full error:', error);
  }

  // Also test basic database connectivity with the URL directly
  if (process.env.DATABASE_URL) {
    const { Pool } = require('pg');

    try {
      const pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: {
          rejectUnauthorized: false // This might be needed for Neon
        }
      });

      const client = await pool.connect();
      console.log('Direct PostgreSQL connection successful!');

      // Check if user table exists
      const result = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables
          WHERE table_schema = 'public'
          AND table_name = 'user'
        );
      `);

      console.log('User table exists:', result.rows[0].exists);

      if (result.rows[0].exists) {
        // Count users
        const userCountResult = await client.query('SELECT COUNT(*) FROM "user";');
        console.log('Number of users in database:', parseInt(userCountResult.rows[0].count));
      }

      client.release();
      await pool.end();
    } catch (directDbError) {
      console.error('Direct PostgreSQL connection failed:', directDbError.message);
    }
  }
}

// Run the test
testBetterAuthConnection().catch(console.error);