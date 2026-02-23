const { neon } = require('@neondatabase/serverless');
const dotenv = require('dotenv');
dotenv.config();

async function checkTables() {
  console.log('Checking current database structure...');

  if (!process.env.DATABASE_URL) {
    console.log('DATABASE_URL not set');
    return;
  }

  const sql = neon(process.env.DATABASE_URL);

  try {
    // List all tables in the database
    const tables = await sql`SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' ORDER BY table_schema, table_name`;
    console.log('Tables in database:');
    for (const row of tables) {
      console.log(`  - ${row.table_schema}.${row.table_name}`);
    }

    // Check if tables exist in public schema specifically
    const pubTables = await sql`SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'`;
    console.log('\nTables in public schema:');
    for (const row of pubTables) {
      console.log(`  - ${row.table_name}`);
    }

    // Check all available schemas
    const schemas = await sql`SELECT schema_name FROM information_schema.schemata ORDER BY schema_name`;
    console.log('\nAvailable schemas:');
    for (const row of schemas) {
      console.log(`  - ${row.schema_name}`);
    }
  } catch (error) {
    console.log('Error checking database structure:', error.message);
  }
}

checkTables().catch(console.error);