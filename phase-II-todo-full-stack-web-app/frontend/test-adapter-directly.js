/**
 * Test the drizzle adapter directly to see if the issue is with the adapter setup
 */
import dotenv from 'dotenv';
dotenv.config();

async function testAdapterDirectly() {
  console.log('Testing drizzle adapter directly...');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    // Create the database connection
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('Direct database connection created');

    // Test the adapter directly
    const adapter = drizzleAdapter(db, {
      provider: "pg",
    });

    console.log('Adapter created:', !!adapter);

    // Check if adapter can access the internal adapter
    console.log('Adapter has internalAdapter:', !!adapter.internalAdapter);
    console.log('Adapter has methods:', Object.keys(adapter || {}));

    // Try to create a user directly through the adapter to see if it works
    const testUser = {
      id: `direct-test-${Date.now()}`,
      email: `adapter-test-${Date.now()}@example.com`,
      emailVerified: false,
      name: 'Adapter Test User',
      image: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    console.log('Attempting to create user via adapter...');

    try {
      const result = await adapter.create({
        model: "user",
        data: testUser
      });

      console.log('Adapter create result:', result);

      // Check if user was actually stored
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('Users after adapter create:', userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > 0) {
        console.log('✓ SUCCESS: Adapter direct creation works!');
      } else {
        console.log('✗ FAILED: Adapter direct creation did not persist');
      }
    } catch (createError) {
      console.log('Adapter create error:', createError.message);
      console.log('Stack:', createError.stack);
    }

  } catch (error) {
    console.error('Adapter test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testAdapterDirectly().catch(console.error);