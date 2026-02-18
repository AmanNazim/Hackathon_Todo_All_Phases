/**
 * Script to check what tables exist in the database
 */
import dotenv from 'dotenv';
dotenv.config();

import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

async function checkTables() {
  console.log('Checking what tables exist in the database...');

  try {
    // Create database connection
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Query to get all table names
    const result = await db.execute(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `);

    console.log('Tables in database:');
    result.rows.forEach(row => {
      console.log('  -', row.table_name);
    });

    if (result.rows.length === 0) {
      console.log('No tables found in the database.');
    }

  } catch (error) {
    console.error('Error checking tables:', error);
  }
}

// Run the check
checkTables().catch(console.error);