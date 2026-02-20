/**
 * Test using the actual getAuth function from src/lib/auth.ts
 */
import dotenv from 'dotenv';
dotenv.config();

async function testActualGetAuth() {
  console.log('=== Testing with Actual getAuth Function ===');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');

    // Create DB connection to check state
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check initial state
    const initialUserCount = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Initial user count:', initialUserCount.rows[0].count);

    // Import and use the actual getAuth function
    console.log('Importing getAuth function...');
    const { getAuth } = await import('./src/lib/auth.js');
    console.log('Calling getAuth()...');
    const auth = await getAuth();

    console.log('Auth object structure:');
    const authKeys = Object.keys(auth);
    console.log('  Keys:', authKeys.slice(0, 10));
    console.log('  has api:', !!auth.api);
    console.log('  has signUpEmail:', typeof auth.api?.signUpEmail);

    const testEmail = `getauth-test-${Date.now()}@example.com`;
    console.log(`Testing registration with: ${testEmail}`);

    try {
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'GetAuth Test User',
        },
        request: new Request('http://localhost:3000/api/auth/sign-up', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: testEmail,
            password: 'TestPassword123!',
            name: 'GetAuth Test User',
          }),
        })
      });

      console.log('Registration result:', {
        success: !!result,
        hasUser: !!result?.user,
        userId: result?.user?.id,
        userEmail: result?.user?.email
      });

      // Check database after registration
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('User count after registration:', userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > initialUserCount.rows[0].count) {
        console.log('✅ SUCCESS: User was actually stored in database!');

        // Get the specific user
        const createdUser = await db.execute(
          'SELECT id, email, name FROM "user" WHERE email = $1',
          [testEmail]
        );

        if (createdUser.rows.length > 0) {
          console.log('Created user:', createdUser.rows[0]);
        }
      } else {
        console.log('❌ FAILED: User was not stored in database');

        // Check if any users exist at all
        const allUsers = await db.execute(
          'SELECT email, "createdAt" FROM "user" ORDER BY "createdAt" DESC LIMIT 5'
        );
        console.log('All users in database:', allUsers.rows);
      }

    } catch (regError) {
      console.log('Registration error:', regError.message);
      console.log('Stack:', regError.stack);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }

  console.log('=== Test Complete ===');
}

testActualGetAuth().catch(console.error);