/**
 * Test to understand Better Auth instance structure
 */
import dotenv from 'dotenv';
dotenv.config();

async function testAdapterStructure() {
  console.log('=== Better Auth Instance Structure Test ===');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    console.log('1. Creating database connection...');
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('2. Creating adapter...');
    const adapter = drizzleAdapter(db, {
      provider: "pg",
    });
    console.log('   Adapter created:', !!adapter);
    console.log('   Adapter type:', typeof adapter);

    console.log('3. Initializing Better Auth...');
    const auth = betterAuth({
      adapter: adapter,
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

    console.log('4. Checking auth structure...');
    console.log('   auth type:', typeof auth);
    console.log('   auth exists:', !!auth);

    // Check main properties
    console.log('   auth.db exists:', !!auth.db);
    console.log('   auth.db type:', typeof auth.db);

    if (auth.db) {
      console.log('   auth.db properties:', Object.keys(auth.db));
      console.log('   auth.db.adapter:', !!auth.db.adapter);
      console.log('   auth.db.adapter type:', typeof auth.db.adapter);
    }

    // Check if better-auth is working differently than expected
    console.log('   auth adapter location might be different...');

    // Check other possible locations for the adapter
    console.log('   auth.internalAdapter:', !!auth.internalAdapter);
    console.log('   auth.$adapter:', !!auth.$adapter);
    console.log('   auth has $user:', !!auth.$user);
    console.log('   auth has $emailPassword:', !!auth.$emailPassword);

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }

  console.log('=== Test Complete ===');
}

testAdapterStructure().catch(console.error);