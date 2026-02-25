import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/ba-schema.ts', // Use Better Auth schema for table creation
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});