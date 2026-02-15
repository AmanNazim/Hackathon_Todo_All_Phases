const { betterAuth } = require("better-auth");
require('dotenv').config();

async function testMinimalConnectionString() {
  console.log('Testing Better Auth with minimal connection string...');

  if (!process.env.DATABASE_URL) {
    console.log('DATABASE_URL not set');
    return;
  }

  console.log('Original URL:', process.env.DATABASE_URL);

  // Try to construct a simpler URL for Better Auth
  const originalUrl = process.env.DATABASE_URL;

  // Parse the URL to understand its components
  try {
    const urlObj = new URL(originalUrl);
    console.log('URL components:');
    console.log('- Protocol:', urlObj.protocol);
    console.log('- Host:', urlObj.hostname);
    console.log('- Port:', urlObj.port);
    console.log('- Username:', urlObj.username);
    console.log('- Password:', urlObj.password ? '[HIDDEN]' : 'none');
    console.log('- Pathname:', urlObj.pathname);
    console.log('- Search params:', urlObj.search);

    // Try to build a cleaner connection string
    let cleanUrl = `${urlObj.protocol}//${urlObj.username}:${urlObj.password}@${urlObj.hostname}${urlObj.port ? ':' + urlObj.port : ''}${urlObj.pathname}`;

    console.log('\nTrying with clean URL:', cleanUrl);

    const auth = betterAuth({
      database: {
        provider: "postgres",
        url: cleanUrl, // Try without query parameters
        autoMigrate: true,
      },
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

    console.log('✓ Better Auth initialized with clean URL!');

    if (auth.db) {
      console.log('✓ Database adapter available with clean URL!');

      try {
        const count = await auth.db.count('user');
        console.log('✓ Connected to database - user count:', count);
      } catch (err) {
        console.log('✗ Could not access database:', err.message);
      }
    } else {
      console.log('✗ Database adapter still not available with clean URL');
    }
  } catch (parseError) {
    console.log('✗ Could not parse URL:', parseError.message);
  }

  // Now try with the original URL that has query parameters
  console.log('\nTrying with original URL (including query parameters)...');
  try {
    const auth2 = betterAuth({
      database: {
        provider: "postgres",
        url: originalUrl, // Original with query parameters
        autoMigrate: true,
      },
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

    console.log('✓ Better Auth initialized with original URL!');

    if (auth2.db) {
      console.log('✓ Database adapter available with original URL!');
    } else {
      console.log('✗ Database adapter not available with original URL');
    }
  } catch (originalError) {
    console.log('✗ Error with original URL:', originalError.message);
  }
}

testMinimalConnectionString().catch(console.error);