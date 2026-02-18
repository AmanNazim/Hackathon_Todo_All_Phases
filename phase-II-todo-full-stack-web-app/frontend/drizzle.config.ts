import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/better-auth-schema.ts', // Point to our Better Auth schema
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  // Enable table creation from schema
  migrations: {
    schema: './src/lib/better-auth-schema.ts',
  },
});