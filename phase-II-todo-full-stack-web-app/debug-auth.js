/**
 * Debug script to check Better Auth configuration
 */
import dotenv from 'dotenv';
dotenv.config();

async function debugAuth() {
  console.log('Environment Variables:');
  console.log('- DATABASE_URL exists:', !!process.env.DATABASE_URL);
  console.log('- BETTER_AUTH_SECRET exists:', !!process.env.BETTER_AUTH_SECRET);
  console.log('- BETTER_AUTH_URL exists:', !!process.env.BETTER_AUTH_URL);
  console.log('- NEXT_PUBLIC_APP_URL exists:', !!process.env.NEXT_PUBLIC_APP_URL);
  console.log('');

  try {
    console.log('Importing auth module...');
    const { getAuth } = await import('./frontend/src/lib/auth');

    console.log('Calling getAuth()...');
    const auth = await getAuth();

    console.log('Auth object keys:', Object.keys(auth).filter(key => !key.startsWith('$')).slice(0, 10));
    console.log('- db exists:', !!auth.db);
    console.log('- db adapter exists:', !!auth.db?.adapter);
    console.log('- session enabled:', !!auth.$session);
    console.log('- emailAndPassword enabled:', !!auth.$emailPassword);

    console.log('\nTesting direct database connection...');
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');

    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    const result = await db.execute('SELECT version();');
    console.log('Direct DB connection works:', !!result);

    const userCount = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('User count via direct connection:', userCount.rows[0].count);

  } catch (error) {
    console.error('Debug error:', error.message);
    console.error('Stack:', error.stack);
  }
}

debugAuth().catch(console.error);