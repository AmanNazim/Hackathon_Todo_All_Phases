const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { Pool } = require('pg');
const { drizzle } = require('drizzle-orm/node-postgres');
require('dotenv').config();

async function testRegistrationFix() {
  console.log('Testing Better Auth registration with fixed Drizzle adapter configuration...');

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

  // Create Drizzle instance from the pool
  const db = drizzle(pool);

  try {
    // Test direct Drizzle connection first
    const result = await db.execute('SELECT 1 as test');
    console.log('✓ Direct Drizzle connection successful!');

    // Initialize Better Auth with the drizzle adapter using the Drizzle instance
    const auth = betterAuth({
      adapter: drizzleAdapter(db, { provider: 'pg' }), // Use drizzle adapter with Drizzle instance
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

    // Check initial user count
    const initialUserCountResult = await db.execute('SELECT COUNT(*) as count FROM "user"');
    const initialUserCount = parseInt(initialUserCountResult.rows[0].count);
    console.log(`Initial user count: ${initialUserCount}`);

    // Try to simulate a registration by creating a user programmatically
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'SecurePass123!';
    const testName = 'Test User';

    console.log(`Creating test user: ${testEmail}`);

    try {
      // Try to create a user using Better Auth's internal API
      const createUserResult = await auth.$context.adapter.create({
        model: 'user',
        data: {
          id: `user_${Date.now()}`,
          email: testEmail,
          name: testName,
          emailVerified: false,
          password: '$2a$10$somehashedpassword', // This is a dummy hash
          createdAt: new Date(),
          updatedAt: new Date(),
        }
      });

      console.log('✓ User created via Better Auth adapter:', createUserResult?.id || 'success');

      // Check user count after creation
      const afterUserCountResult = await db.execute('SELECT COUNT(*) as count FROM "user"');
      const afterUserCount = parseInt(afterUserCountResult.rows[0].count);
      console.log(`User count after creation: ${afterUserCount}`);

      if (afterUserCount > initialUserCount) {
        console.log('🎉 SUCCESS: User was successfully saved to the database!');

        // Fetch the created user to verify
        const usersResult = await db.execute('SELECT id, email, name FROM "user" ORDER BY created_at DESC LIMIT 1');
        if (usersResult.rows.length > 0) {
          const user = usersResult.rows[0];
          console.log(`Verified user in DB: ${user.email}`);
        }
      } else {
        console.log('❌ ISSUE: User count did not increase - data not persisted to DB');
      }
    } catch (createErr) {
      console.log('⚠ User creation failed:', createErr.message);
    }

  } catch (error) {
    console.log('✗ Error during testing:', error.message);
    console.log('Full error:', error);
  }

  await pool.end();
}

testRegistrationFix().catch(console.error);