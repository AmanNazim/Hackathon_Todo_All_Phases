import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/app-schema.ts', // For application-specific tables migration only
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});