/**
 * Test to simulate a registration flow and see what happens
 */
import dotenv from 'dotenv';
dotenv.config();

async function testRegistrationSimulation() {
  console.log('Testing registration simulation...');

  try {
    // Direct database test to check current state
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');

    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check the user table directly
    const userCountBefore = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Users before test:', userCountBefore.rows[0].count);

    // Now try to import and use Better Auth directly for user creation
    // This will help us understand if the adapter is working
    console.log('Attempting to initialize auth...');

    // Use the auth.ts file (the one used by the API route) to get the auth instance
    const { default: auth } = await import('./auth.js');

    if (!auth) {
      console.log('ERROR: Could not load auth instance from auth.ts');
      return;
    }

    console.log('Auth instance loaded from auth.ts');
    console.log('Auth has database:', !!auth.db);
    console.log('Auth has emailPassword:', !!auth.$emailPassword);

    // Try to create a user directly through the Better Auth API
    try {
      const testEmail = `test-${Date.now()}@example.com`;
      console.log(`Attempting to create user: ${testEmail}`);

      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Test User'
        },
        request: new Request('http://localhost:3000/api/auth/sign-up', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      });

      console.log('Registration result:', result);
    } catch (regError) {
      console.log('Registration error:', regError.message);
      console.log('Error stack:', regError.stack);
    }

    // Check if there are now any users
    const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Users after registration attempt:', userCountAfter.rows[0].count);

    if (userCountAfter.rows[0].count > userCountBefore.rows[0].count) {
      console.log('✓ SUCCESS: Users were created in the database!');
      const users = await db.execute('SELECT id, email, name FROM "user" ORDER BY "createdAt" DESC LIMIT 5;');
      console.log('New users:');
      users.rows.forEach(user => {
        console.log(`  - ${user.id}: ${user.email} (${user.name})`);
      });
    } else {
      console.log('✗ FAILED: No new users were created');
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testRegistrationSimulation().catch(console.error);