/**
 * Test to see the actual structure of the Better Auth object
 */
import dotenv from 'dotenv';
dotenv.config();

async function testActualAuthObject() {
  console.log('=== Better Auth Full Object Test ===');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    console.log('1. Creating database connection...');
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('2. Initializing Better Auth...');
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

    console.log('3. Full auth object keys (first 20):');
    const authKeys = Object.keys(auth);
    console.log('   Keys:', authKeys.slice(0, 20));
    console.log('   Total keys:', authKeys.length);

    // Check for some of the expected API methods
    console.log('4. Checking for API methods...');
    console.log('   auth.api exists:', !!auth.api);
    console.log('   auth.api.signUpEmail:', typeof auth.api?.signUpEmail);

    if (auth.api) {
      console.log('   auth.api keys:', Object.keys(auth.api).slice(0, 10));
    }

    // Check for other possible property names
    console.log('5. Checking other potential properties...');
    const potentialProperties = [
      'db', 'database', 'adapter', 'internalAdapter', '$user', '$session',
      '$emailPassword', 'session', 'user', 'account'
    ];

    potentialProperties.forEach(prop => {
      console.log(`   auth.${prop}:`, typeof auth[prop], !!auth[prop]);
    });

    // Let's try a simple registration to see if we can get more information
    const testEmail = `test-structure-${Date.now()}@example.com`;
    console.log(`6. Testing registration with email: ${testEmail}`);

    try {
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Structure Test User',
        },
        request: new Request('http://localhost:3000/api/auth/sign-up', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: testEmail,
            password: 'TestPassword123!',
            name: 'Structure Test User',
          }),
        })
      });

      console.log('   Registration result:', {
        hasResult: !!result,
        hasUser: !!result?.user,
        userId: result?.user?.id,
        userEmail: result?.user?.email
      });
    } catch (regError) {
      console.log('   Registration error:', regError.message);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }

  console.log('=== Test Complete ===');
}

testActualAuthObject().catch(console.error);