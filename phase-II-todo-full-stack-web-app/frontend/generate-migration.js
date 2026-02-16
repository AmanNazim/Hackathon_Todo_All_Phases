/**
 * Script to generate Drizzle migrations for Better Auth tables
 */
import { defineConfig } from 'drizzle-kit';
import { execSync } from 'child_process';

const config = defineConfig({
  schema: './src/lib/better-auth-schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL || process.env.NEXT_PUBLIC_DATABASE_URL || '',
  },
});

console.log('Generating Drizzle migrations for Better Auth tables...');
console.log('DATABASE_URL:', process.env.DATABASE_URL ? 'Set' : 'Not set');

try {
  // Generate migration
  execSync('npx drizzle-kit generate', { stdio: 'inherit', cwd: process.cwd() });
  console.log('✓ Migration files generated successfully');
} catch (error) {
  console.error('✗ Error generating migration:', error.message);
}