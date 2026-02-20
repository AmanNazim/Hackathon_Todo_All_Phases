/**
 * Complete test of the registration flow to identify where it fails
 */
import dotenv from 'dotenv';
dotenv.config();

async function testCompleteRegistrationFlow() {
  console.log('=== Complete Registration Flow Test ===');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    console.log('1. Creating database connection...');
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check initial state
    const initialUserCount = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('   Initial user count:', initialUserCount.rows[0].count);

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

    console.log('3. Checking adapter configuration...');
    console.log('   Auth has adapter:', !!auth.db?.adapter);
    console.log('   Auth adapter type:', typeof auth.db?.adapter);

    const testEmail = `complete-test-${Date.now()}@example.com`;
    console.log('4. Attempting registration for:', testEmail);

    // Test the API endpoint directly
    const request = new Request('http://localhost:3000/api/auth/sign-up', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: testEmail,
        password: 'TestPassword123!',
        name: 'Complete Test User',
      }),
    });

    try {
      console.log('5. Calling auth.api.signUpEmail...');
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Complete Test User',
        },
        request: request,
      });

      console.log('6. Registration API result:', {
        success: !!result,
        hasUser: !!result?.user,
        userEmail: result?.user?.email,
        userId: result?.user?.id
      });

      // Check immediately after the call
      console.log('7. Checking database immediately after registration...');
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('   User count after registration:', userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > initialUserCount.rows[0].count) {
        console.log('   ✅ SUCCESS: User was stored in database!');

        // Get the specific user
        const createdUser = await db.execute(
          'SELECT id, email, name, "createdAt" FROM "user" WHERE email = $1',
          [testEmail]
        );

        if (createdUser.rows.length > 0) {
          console.log('   Created user details:', createdUser.rows[0]);
        }
      } else {
        console.log('   ❌ FAILED: User not found in database');

        // Let's also check all users to see if there are any at all
        const allUsers = await db.execute(
          'SELECT email, "createdAt" FROM "user" ORDER BY "createdAt" DESC LIMIT 10'
        );
        console.log('   All users in database:', allUsers.rows);

        // Test direct insert to verify that basic database operations work
        try {
          console.log('8. Testing direct database insert...');
          await db.execute(`
            INSERT INTO "user" (id, email, "emailVerified", name, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6)
          `, [
            `direct-test-${Date.now()}`,
            `direct-${testEmail}`,
            false,
            'Direct Test User',
            new Date(),
            new Date()
          ]);

          console.log('   Direct insert succeeded');

          const directUserCheck = await db.execute('SELECT COUNT(*) as count FROM "user";');
          console.log('   User count after direct insert:', directUserCheck.rows[0].count);

          // Clean up the direct insert
          await db.execute('DELETE FROM "user" WHERE email = $1', [`direct-${testEmail}`]);
          console.log('   Direct test user cleaned up');
        } catch (directError) {
          console.log('   Direct insert failed:', directError.message);
        }
      }

    } catch (regError) {
      console.log('5. Registration failed:', regError.message);
      console.log('   Error stack:', regError.stack);
    }

  } catch (error) {
    console.error('Test setup failed:', error.message);
    console.error('Stack:', error.stack);
  }

  console.log('=== Test Complete ===');
}

testCompleteRegistrationFlow().catch(console.error);