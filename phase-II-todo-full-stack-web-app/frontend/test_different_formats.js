const { betterAuth } = require("better-auth");
require('dotenv').config();

async function testDifferentConnectionFormats() {
  console.log('Testing different database connection formats...');

  let originalDbUrl = process.env.DATABASE_URL;
  console.log('Original DATABASE_URL:', originalDbUrl);

  // Different variations to test
  const urlsToTest = [
    originalDbUrl, // Original
    originalDbUrl.replace('?sslmode=require', '?sslmode=verify-full'), // More explicit SSL
    originalDbUrl.replace('sslmode=require', 'sslmode=require').replace('&channel_binding=require', ''), // Without channel binding
    originalDbUrl.replace(/channel_binding=require&?/, ''), // Remove channel binding completely
    originalDbUrl + '&sslmode=verify-full', // Add explicit verify-full
  ];

  for (let i = 0; i < urlsToTest.length; i++) {
    const testUrl = urlsToTest[i];
    console.log(`\n--- Testing URL ${i + 1}: ${testUrl} ---`);

    try {
      const auth = betterAuth({
        database: testUrl ? {
          provider: "postgres",
          url: testUrl,
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

      console.log(`✓ Better Auth initialized successfully for URL ${i + 1}`);

      if (auth.db) {
        console.log(`✓ Database adapter available for URL ${i + 1}`);

        try {
          const userCount = await auth.db.count('user');
          console.log(`✓ Database connection verified for URL ${i + 1} - user count: ${userCount}`);
          break; // Found a working configuration
        } catch (countErr) {
          console.log(`✗ Could not access user table for URL ${i + 1}:`, countErr.message);
        }
      } else {
        console.log(`✗ Database adapter not available for URL ${i + 1}`);
      }
    } catch (error) {
      console.log(`✗ Error with URL ${i + 1}:`, error.message);
    }
  }
}

testDifferentConnectionFormats().catch(console.error);