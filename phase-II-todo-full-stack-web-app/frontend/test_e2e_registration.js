const { betterAuth } = require("better-auth");
const { toNextJsHandler } = require("better-auth/next-js");
require('dotenv').config();

async function testEndToEndRegistration() {
  console.log('=== END-TO-END REGISTRATION TEST ===');
  console.log('Environment variables:');
  console.log('- DATABASE_URL:', process.env.DATABASE_URL ? 'SET' : 'NOT SET');
  console.log('- BETTER_AUTH_SECRET:', process.env.BETTER_AUTH_SECRET ? 'SET' : 'NOT SET');
  console.log('');

  try {
    // Initialize Better Auth with database
    console.log('Initializing Better Auth with database...');

    const auth = betterAuth({
      database: process.env.DATABASE_URL ? {
        provider: "postgres",
        url: process.env.DATABASE_URL,
        autoMigrate: true, // Enable automatic table creation/migration
      } : undefined,
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // 1 day
      },
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    console.log('✓ Better Auth initialized');

    // Check if database adapter is available
    if (!auth.db) {
      console.log('✗ Database adapter not available - this is the issue!');
      throw new Error('Database adapter not available');
    }

    console.log('✓ Database adapter available');

    // Try to count users before registration
    let userCountBefore = 0;
    try {
      userCountBefore = await auth.db.count('user');
      console.log(`✓ Users before registration: ${userCountBefore}`);
    } catch (countError) {
      console.log(`✗ Could not count users before registration:`, countError.message);
    }

    // Generate test user data
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'SecurePass123!';
    const testName = 'Test User';

    console.log(`Attempting to register user: ${testEmail}`);

    // Attempt to create a user using Better Auth's internal methods
    try {
      // Try to register using the auth API directly
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

      console.log('Registration API call result:', result);

      if (result?.session) {
        console.log('✓ Registration successful!');
        console.log('- Session created:', !!result.session);
        console.log('- User ID:', result.session.userId);
      } else if (result?.error) {
        console.log('✗ Registration failed with error:', result.error);
      } else {
        console.log('✗ Unexpected registration result:', result);
      }
    } catch (regError) {
      console.log('✗ Registration API call failed with error:', regError.message);
      console.log('Full error:', regError);
    }

    // Check if user was created in database
    try {
      const userCountAfter = await auth.db.count('user');
      console.log(`✓ Users after registration: ${userCountAfter}`);

      if (userCountAfter > userCountBefore) {
        console.log('🎉 SUCCESS: User was created in database!');

        // Try to fetch the newly created user
        const users = await auth.db.findMany('user', {});
        console.log(`Found ${users.length} user(s) in database:`);
        for (const user of users) {
          console.log(`- ID: ${user.id}, Email: ${user.email}, Name: ${user.name}`);
        }
      } else {
        console.log('❌ ISSUE: No new user was created in database despite registration attempt');
      }
    } catch (afterCountError) {
      console.log('✗ Could not count users after registration:', afterCountError.message);
    }

  } catch (error) {
    console.log('❌ FATAL ERROR in test:', error.message);
    console.log('Full error:', error);
  }

  console.log('\n=== TEST COMPLETE ===');
}

// Run the test
testEndToEndRegistration().catch(console.error);