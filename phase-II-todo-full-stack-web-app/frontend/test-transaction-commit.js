/**
 * Test to verify if registration transaction commits properly
 */
import dotenv from 'dotenv';
dotenv.config();

async function testTransactionCommit() {
  console.log('Testing registration with immediate database check...');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check user count before
    const userCountBefore = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Users before registration:', userCountBefore.rows[0].count);

    // Initialize Better Auth with the drizzle adapter
    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg",
      }),
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
      },
      plugins: [],
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    console.log('Better Auth initialized, attempting to create a user...');

    const testEmail = `transaction-test-${Date.now()}@example.com`;

    // Create a mock request object for the registration
    const mockRequest = new Request('http://localhost:3000/api/auth/sign-up', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: testEmail,
        password: 'TestPassword123!',
        name: 'Transaction Test User',
      }),
    });

    try {
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Transaction Test User',
        },
        request: mockRequest,
      });

      console.log('Registration API result:', result?.user?.email);

      // Immediately check the database again
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('Users after registration API call:', userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > userCountBefore.rows[0].count) {
        // Get the newly created user
        const newUser = await db.execute(`
          SELECT id, email, name, "createdAt"
          FROM "user"
          WHERE email = $1
          ORDER BY "createdAt" DESC
          LIMIT 1
        `, [testEmail]);

        if (newUser.rows.length > 0) {
          console.log('✓ SUCCESS: User was created and committed to database!');
          console.log('Created user:', newUser.rows[0]);
        } else {
          console.log('✗ User count increased but user not found');
        }
      } else {
        console.log('✗ FAILED: Transaction was not committed to database');

        // Double check by querying recent users anyway
        const allUsers = await db.execute(`
          SELECT id, email, name, "createdAt"
          FROM "user"
          ORDER BY "createdAt" DESC
          LIMIT 5
        `);

        console.log('All users in database:', allUsers.rows);
      }
    } catch (signUpError) {
      console.log('Registration error:', signUpError.message);
      console.log('Stack:', signUpError.stack);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testTransactionCommit().catch(console.error);