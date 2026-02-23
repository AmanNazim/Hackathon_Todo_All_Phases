import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { neon, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import dotenv from 'dotenv';
dotenv.config();

async function testAuthAfterFix() {
  console.log('Testing Better Auth registration after migration fix...');

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

    // Initialize Better Auth with the corrected config
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
      plugins: [],
      secret: process.env.BETTER_AUTH_SECRET || 'dev-secret-change-in-production',
      baseURL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      trustedOrigins: [
        process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      ],
      advanced: {
        useSecureCookies: false,
        defaultCookieAttributes: {
          sameSite: "lax",
        },
      },
    });

    console.log('✓ Better Auth initialized!');

    // Check if tables exist now
    try {
      const result = await sql`SELECT COUNT(*) as count FROM "user"`;
      console.log(`✓ Users table exists! Current user count: ${parseInt(result[0].count)}`);
    } catch (e) {
      console.log(`✗ Users table may not exist: ${e.message}`);
      return;
    }

    // Test registration
    const testEmail = `test_${Date.now()}@example.com`;
    const testPassword = 'SecurePass123!';
    const testName = 'Test User';

    console.log(`Registering new user: ${testEmail}`);

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

    console.log('Registration result:', result);

    if (result?.user && result?.user?.id) {
      console.log('✓ Registration successful!');
      console.log('  - User ID:', result.user.id);
      console.log('  - User Email:', result.user.email);

      // Verify that the user was saved in the database
      const userCheck = await sql`SELECT id, email, name FROM "user" WHERE email = ${testEmail}`;
      if (userCheck.length > 0) {
        console.log('✓ User found in database:', userCheck[0].email);
        console.log('🎉 Registration data persistence SUCCESS!');
      } else {
        console.log('✗ User was not saved to database even though creation succeeded');
      }
    } else if (result?.error) {
      console.log('✗ Registration failed:', result.error);
    } else {
      console.log('⚠ No user data in result, but checking for user in DB...');
      // Even if no user in result, check database
      const userCheck = await sql`SELECT id, email, name FROM "user" WHERE email = ${testEmail}`;
      if (userCheck.length > 0) {
        console.log('✓ User found in database:', userCheck[0].email);
        console.log('🎉 Registration data persistence SUCCESS!');
      } else {
        console.log('✗ User not found in database');
      }
    }

  } catch (error) {
    console.log('✗ Error during testing:', error.message);
    console.log('Full error:', error);
  }
}

testAuthAfterFix().catch(console.error);