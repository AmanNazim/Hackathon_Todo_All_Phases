/**
 * Test direct database write to check if the database connection works properly
 */
import dotenv from 'dotenv';
dotenv.config();

async function testDirectDatabaseWrite() {
  console.log('Testing direct database write...');

  try {
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');

    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check user count before
    const userCountBefore = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Users before direct test:', userCountBefore.rows[0].count);

    // Try to insert a test user directly (this would bypass Better Auth entirely)
    // This is just to test if the database itself is working
    const testUserId = `test-user-${Date.now()}`;
    const testEmail = `direct-test-${Date.now()}@example.com`;

    try {
      const insertResult = await db.execute(`
        INSERT INTO "user" (id, email, "emailVerified", name, "createdAt", "updatedAt")
        VALUES ($1, $2, false, 'Direct Test User', NOW(), NOW())
        RETURNING id, email
      `, [testUserId, testEmail]);

      console.log('Direct insert result:', insertResult);

      // Check user count after direct insert
      const userCountAfterDirect = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log('Users after direct insert:', userCountAfterDirect.rows[0].count);

      if (userCountAfterDirect.rows[0].count > userCountBefore.rows[0].count) {
        console.log('✓ Direct database write works - database connection is fine');

        // Clean up the test user
        await db.execute('DELETE FROM "user" WHERE email = $1', [testEmail]);
        console.log('Test user cleaned up');
      } else {
        console.log('✗ Direct database write failed');
      }
    } catch (insertError) {
      console.log('Direct insert error (this is expected if there are constraints):', insertError.message);
    }

    // Check if Better Auth tables have the expected structure
    console.log('\nChecking user table structure...');
    try {
      const tableInfo = await db.execute(`
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position;
      `);

      console.log('User table columns:');
      tableInfo.rows.forEach(col => {
        console.log(`  - ${col.column_name}: ${col.data_type} (${col.is_nullable === 'YES' ? 'nullable' : 'not nullable'})`);
      });
    } catch (infoError) {
      console.log('Could not get table info:', infoError.message);
    }

  } catch (error) {
    console.error('Test error:', error.message);
    console.error('Stack:', error.stack);
  }
}

testDirectDatabaseWrite().catch(console.error);