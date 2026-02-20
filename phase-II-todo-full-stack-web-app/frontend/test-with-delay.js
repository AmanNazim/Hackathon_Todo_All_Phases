/**
 * Test registration with delay to see if transaction just takes time to commit
 */
import dotenv from 'dotenv';
dotenv.config();

async function testWithDelay() {
  console.log('=== Registration Test with Delay ===');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check initial state
    const initialUserCount = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Initial user count:', initialUserCount.rows[0].count);

    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg",
      }),
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7,
        updateAge: 60 * 60 * 24,
      },
      plugins: [],
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    const testEmail = `delay-test-${Date.now()}@example.com`;
    console.log(`Registering user: ${testEmail}`);

    const result = await auth.api.signUpEmail({
      body: {
        email: testEmail,
        password: 'TestPassword123!',
        name: 'Delay Test User',
      },
      request: new Request('http://localhost:3000/api/auth/sign-up', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Delay Test User',
        }),
      })
    });

    console.log('Registration result:', {
      hasUser: !!result?.user,
      userId: result?.user?.id,
      userEmail: result?.user?.email
    });

    // Check immediately
    const userCountImmediate = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('User count immediately after:', userCountImmediate.rows[0].count);

    // Wait a bit and check again
    console.log('Waiting 1 second before checking again...');
    await new Promise(resolve => setTimeout(resolve, 1000));

    const userCountAfterDelay = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('User count after 1 second:', userCountAfterDelay.rows[0].count);

    // Wait more
    console.log('Waiting additional 2 seconds...');
    await new Promise(resolve => setTimeout(resolve, 2000));

    const userCountAfterLonger = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('User count after 3 seconds total:', userCountAfterLonger.rows[0].count);

    // Try a direct query for the specific user
    const specificUserCheck = await db.execute(
      'SELECT id, email, name FROM "user" WHERE email = $1',
      [testEmail]
    );
    console.log('Specific user found:', specificUserCheck.rows.length, 'records');
    if (specificUserCheck.rows.length > 0) {
      console.log('User details:', specificUserCheck.rows[0]);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }

  console.log('=== Test Complete ===');
}

testWithDelay().catch(console.error);