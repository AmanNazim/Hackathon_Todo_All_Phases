const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { Pool } = require('pg');
const { drizzle } = require('drizzle-orm/node-postgres');
require('dotenv').config();

async function testTableCreation() {
  console.log('Testing Better Auth table creation and user persistence...');

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

  // Create Drizzle instance
  const db = drizzle(pool);

  try {
    // Test direct Drizzle connection first
    const result = await db.execute('SELECT 1 as test');
    console.log('✓ Direct Drizzle connection successful!');

    // Check existing tables
    const tablesResult = await db.execute(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
    `);
    console.log('Available tables:', tablesResult.rows.map(r => r.table_name));

    // Check if Better Auth tables exist
    const betterAuthTables = [
      'user', 'session', 'account', 'verification'
    ];

    for (const table of betterAuthTables) {
      try {
        const countResult = await db.execute(`SELECT COUNT(*) as count FROM "${table}"`);
        console.log(`${table} table - Count: ${parseInt(countResult.rows[0].count)}`);
      } catch (err) {
        console.log(`${table} table - Does not exist: ${err.message}`);
      }
    }

    // Now try to initialize Better Auth with the drizzle adapter
    const auth = betterAuth({
      adapter: drizzleAdapter(db, { provider: 'pg' }),
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

    // Try to create a test user programmatically
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'SecurePass123!';
    const testName = 'Test User';

    console.log(`Creating test user: ${testEmail}`);

    try {
      // Attempt to create user directly through Better Auth's database interface
      const newUser = await auth.context.prismaClient.user.create({
        data: {
          id: `user_${Date.now()}`,
          email: testEmail,
          name: testName,
          emailVerified: false,
          createdAt: new Date(),
          updatedAt: new Date(),
        }
      });
      console.log('✓ User created via direct DB call:', newUser.id);
    } catch (directCreateErr) {
      console.log('⚠ Direct DB creation failed (expected if using different ORM):', directCreateErr.message);
    }

    // Check user count after attempted creation
    try {
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user"');
      console.log('User count after creation attempt:', parseInt(userCountAfter.rows[0].count));
    } catch (countErr) {
      console.log('Could not count users after creation:', countErr.message);
    }

  } catch (error) {
    console.log('✗ Error during testing:', error.message);
    console.log('Full error:', error);
  }

  await pool.end();
}

testTableCreation().catch(console.error);