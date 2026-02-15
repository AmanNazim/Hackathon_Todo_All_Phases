const { betterAuth } = require("better-auth");
require('dotenv').config();

async function testBetterAuthConnectionFixed() {
  console.log('Testing Better Auth database connection with fixed parameters...');

  // Extract the base URL without problematic parameters
  let originalDbUrl = process.env.DATABASE_URL;
  console.log('Original DATABASE_URL:', originalDbUrl);

  // Try removing channel_binding which might not be supported by Better Auth
  let fixedDbUrl = originalDbUrl;
  if (originalDbUrl.includes('channel_binding=require')) {
    fixedDbUrl = originalDbUrl.replace('&channel_binding=require', '');
    console.log('Fixed DATABASE_URL (removed channel_binding):', fixedDbUrl);
  }

  try {
    // Initialize Better Auth with the corrected database configuration
    const auth = betterAuth({
      database: fixedDbUrl ? {
        provider: "postgres",
        url: fixedDbUrl,
        autoMigrate: true,
      } : undefined,
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7,
        updateAge: 60 * 60 * 24,
      },
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
    });

    console.log('Better Auth initialized successfully!');

    if (auth.db) {
      console.log('Database adapter available - connection successful!');

      // Try to count users
      try {
        const userCount = await auth.db.count('user');
        console.log('Database connection verified - user count:', userCount);

        // Try to create a test user to verify write capability
        console.log('Attempting to create a test user...');
        // Note: This is just to test if writes work, we won't actually create a user
      } catch (countErr) {
        console.log('Could not access user table:', countErr.message);
      }
    } else {
      console.log('Database adapter still not available - connection failed');
    }

  } catch (error) {
    console.error('Error initializing Better Auth:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

testBetterAuthConnectionFixed().catch(console.error);