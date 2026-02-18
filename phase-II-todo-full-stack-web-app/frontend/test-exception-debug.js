/**
 * Debug registration to catch any silent exceptions
 */
import dotenv from 'dotenv';
dotenv.config();

async function testExceptionDebug() {
  console.log('Debugging registration for any exceptions...');

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
      // Add comprehensive hooks to catch what's happening
      databaseHooks: {
        user: {
          create: {
            before: async ({ data, ctx }) => {
              console.log("DB Hook: Before user creation -", data.email);
              return data;
            },
            after: async ({ data, ctx }) => {
              console.log("DB Hook: After user creation -", data.email);
            }
          }
        }
      },
      hooks: {
        after: [
          {
            matcher: (path) => path.includes('/sign-up'),
            handler: (ctx) => {
              console.log("API Hook: After sign-up called", ctx.context.returned);
            }
          }
        ]
      }
    });

    const testEmail = `debug-test-${Date.now()}@example.com`;

    const request = new Request('http://localhost:3000/api/auth/sign-up', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: testEmail,
        password: 'TestPassword123!',
        name: 'Debug Test User',
      }),
    });

    console.log('Making registration request...');

    try {
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Debug Test User',
        },
        request: request,
      });

      console.log('API result:', JSON.stringify(result, null, 2));

      // Wait a bit to ensure any async operations complete
      await new Promise(resolve => setTimeout(resolve, 500));

      // Check if user was actually stored
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('Users after registration:', userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > userCountBefore.rows[0].count) {
        console.log('✓ SUCCESS: User was actually stored in database!');
      } else {
        console.log('✗ FAILED: User was not stored in database');

        // Let's try to query for the user by email to be sure
        const specificUser = await db.execute(
          'SELECT id, email FROM "user" WHERE email = $1',
          [testEmail]
        );

        if (specificUser.rows.length > 0) {
          console.log('User found with specific query:', specificUser.rows[0]);
        } else {
          console.log('User not found in database at all');
        }
      }
    } catch (error) {
      console.log('Registration API error:', error.message);
      console.log('Error stack:', error.stack);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testExceptionDebug().catch(console.error);