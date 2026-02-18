/**
 * Test Better Auth initialization directly by importing the actual auth function
 * Since we can't import TypeScript files directly in Node.js, let's check the configuration differently
 */
import dotenv from 'dotenv';
dotenv.config();

async function testAuthConfig() {
  console.log('Testing Better Auth configuration...');

  console.log('Environment variables:');
  console.log('- DATABASE_URL set:', !!process.env.DATABASE_URL);
  console.log('- BETTER_AUTH_SECRET set:', !!process.env.BETTER_AUTH_SECRET);
  console.log('- BETTER_AUTH_URL set:', !!process.env.BETTER_AUTH_URL);
  console.log('- NEXT_PUBLIC_APP_URL set:', !!process.env.NEXT_PUBLIC_APP_URL);

  // Now let's check if we can test just the connection part
  try {
    console.log('\nTesting database connection...');
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    // Test if we can create the database connection and adapter
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    console.log('✓ Database connection successful');

    // Test if the adapter can be created (without Better Auth initialization)
    const adapter = drizzleAdapter(db, {
      provider: "pg",
      // No custom schema - let Better Auth manage internally
    });

    console.log('✓ Drizzle adapter created successfully');

    // Check if the database has the expected Better Auth tables
    const result = await db.execute(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
      ORDER BY table_name;
    `);

    console.log('Better Auth tables found:', result.rows.map(r => r.table_name).join(', '));

    // Check if any rows exist in these tables
    const tables = ['user', 'session', 'account', 'verification'];
    for (const table of tables) {
      try {
        const countResult = await db.execute(`SELECT COUNT(*) as count FROM "${table}";`);
        console.log(`${table} table has ${countResult.rows[0].count} records`);
      } catch (err) {
        console.log(`Error checking ${table} table:`, err.message);
      }
    }

  } catch (error) {
    console.error('Configuration test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testAuthConfig().catch(console.error);