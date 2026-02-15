require('dotenv').config();

async function testDirectConnection() {
  console.log('Testing direct database connection...');

  if (!process.env.DATABASE_URL) {
    console.log('DATABASE_URL not set');
    return;
  }

  const { Pool } = require('pg');

  const testUrls = [
    process.env.DATABASE_URL,
    process.env.DATABASE_URL.replace('&channel_binding=require', ''),
    process.env.DATABASE_URL.replace('sslmode=require', 'sslmode=verify-full'),
  ];

  for (let i = 0; i < testUrls.length; i++) {
    console.log(`\n--- Testing direct connection with URL ${i + 1} ---`);
    console.log('URL:', testUrls[i]);

    try {
      const pool = new Pool({
        connectionString: testUrls[i],
        ssl: {
          rejectUnauthorized: false // Needed for Neon
        }
      });

      const client = await pool.connect();
      console.log('✓ Direct PostgreSQL connection successful!');

      // Check if user table exists
      const result = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables
          WHERE table_schema = 'public'
          AND table_name = 'user'
        );
      `);

      console.log('User table exists:', result.rows[0].exists);

      if (result.rows[0].exists) {
        const userCountResult = await client.query('SELECT COUNT(*) FROM "user";');
        console.log('Number of users in database:', parseInt(userCountResult.rows[0].count));
      } else {
        console.log('User table does not exist yet');
      }

      client.release();
      await pool.end();
      console.log('✓ Connection test completed successfully');
      break;
    } catch (directDbError) {
      console.log('✗ Direct PostgreSQL connection failed:', directDbError.message);
    }
  }
}

testDirectConnection().catch(console.error);