/**
 * Script to test if registration data is actually being stored
 */
import dotenv from 'dotenv';
dotenv.config();

import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

async function testRegistrationData() {
  console.log('Testing registration data storage...');

  try {
    // Create database connection
    const sql = neon(process.env.DATABASE_URL);
    const db = drizzle(sql);

    // Check if any users exist in the Better Auth user table
    const userResult = await db.execute('SELECT COUNT(*) as count FROM "user";');
    console.log('Number of users in user table:', userResult.rows[0].count);

    // If users exist, get some user details
    if (userResult.rows[0].count > 0) {
      const users = await db.execute('SELECT id, email, name, "createdAt" FROM "user" LIMIT 5;');
      console.log('Sample users:');
      users.rows.forEach((row, index) => {
        console.log(`  ${index + 1}. ID: ${row.id}, Email: ${row.email}, Name: ${row.name}, Created: ${row.createdAt}`);
      });

      // Check if there are any tasks associated with these users
      const taskResult = await db.execute('SELECT COUNT(*) as count FROM "tasks";');
      console.log('Number of tasks in tasks table:', taskResult.rows[0].count);

      if (taskResult.rows[0].count > 0) {
        const tasks = await db.execute('SELECT id, user_id, title, "createdAt" FROM "tasks" LIMIT 5;');
        console.log('Sample tasks:');
        tasks.rows.forEach((row, index) => {
          console.log(`  ${index + 1}. ID: ${row.id}, User ID: ${row.user_id}, Title: ${row.title}, Created: ${row.createdAt}`);
        });
      }
    }

    // Check application-specific tables
    const tablesToCheck = [
      { name: 'user_preferences', label: 'User Preferences' },
      { name: 'task_history', label: 'Task History' },
      { name: 'task_tags', label: 'Task Tags' },
      { name: 'password_reset_tokens', label: 'Password Reset Tokens' },
      { name: 'email_verification_tokens', label: 'Email Verification Tokens' },
      { name: 'daily_analytics', label: 'Daily Analytics' },
      { name: 'analytics_cache', label: 'Analytics Cache' }
    ];

    for (const table of tablesToCheck) {
      try {
        const result = await db.execute(`SELECT COUNT(*) as count FROM "${table.name}";`);
        console.log(`Number of ${table.label}:`, result.rows[0].count);
      } catch (error) {
        console.log(`Error checking ${table.name}:`, error.message);
      }
    }

  } catch (error) {
    console.error('Error in registration data test:', error);
  }
}

// Run the test
testRegistrationData().catch(console.error);