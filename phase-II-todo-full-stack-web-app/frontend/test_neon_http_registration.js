const { betterAuth } = require('better-auth');
const { drizzleAdapter } = require('better-auth/adapters/drizzle');
const { neon, neonConfig } = require('@neondatabase/serverless');
const { drizzle } = require('drizzle-orm/neon-http');
require('dotenv').config();

async function testNeonHttpRegistration() {
  console.log('Testing Better Auth registration with Neon HTTP client...');

  if (!process.env.DATABASE_URL) {
    console.log('DATABASE_URL not set');
    return;
  }

  try {
    // Configure Neon for serverless compatibility
    neonConfig.fetchConnectionCache = true;

    // Create Neon HTTP client
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('✓ Neon HTTP client created successfully!');

    // Initialize Better Auth with the drizzle adapter using the Neon HTTP client
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

    console.log('✓ Better Auth initialized with Neon HTTP client!');

    // Check initial user count
    const initialUserCountResult = await sql('SELECT COUNT(*) as count FROM "user"');
    const initialUserCount = parseInt(initialUserCountResult[0].count);
    console.log(`Initial user count: ${initialUserCount}`);

    // Simulate a registration request
    const testEmail = `test_user_${Date.now()}@example.com`;
    const testPassword = 'SecurePass123!';
    const testName = 'Test User';

    console.log(`Simulating registration for: ${testEmail}`);

    try {
      // Use Better Auth's internal registration API
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: testPassword,
          name: testName,
        },
        headers: {
          'content-type': 'application/json',
        },
      });

      console.log('Registration API result:', result);

      if (result?.session) {
        console.log('✓ Registration successful!');
        console.log('  - Session created:', !!result.session);
        console.log('  - User ID:', result.session.userId);

        // Check user count after successful registration
        const afterUserCountResult = await sql('SELECT COUNT(*) as count FROM "user"');
        const afterUserCount = parseInt(afterUserCountResult[0].count);
        console.log(`User count after registration: ${afterUserCount}`);

        if (afterUserCount > initialUserCount) {
          console.log('🎉 SUCCESS: User was successfully saved to the database!');

          // Fetch the created user to verify
          const usersResult = await sql('SELECT id, email, name, created_at FROM "user" WHERE email = $1', [testEmail]);
          if (usersResult.length > 0) {
            const user = usersResult[0];
            console.log(`Verified user in DB: ${user.email} (${user.id})`);
          }
        } else {
          console.log('❌ ISSUE: Registration succeeded but user was not saved to database');
        }
      } else if (result?.error) {
        console.log('✗ Registration failed with error:', result.error);
      } else {
        console.log('⚠ Unexpected registration result:', result);
      }
    } catch (regError) {
      console.log('✗ Registration API call failed:', regError.message);
      console.log('Full error:', regError);
    }

  } catch (error) {
    console.log('✗ Error during testing:', error.message);
    console.log('Full error:', error);
  }
}

testNeonHttpRegistration().catch(console.error);