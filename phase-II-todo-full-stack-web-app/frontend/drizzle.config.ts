import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/app-schema.ts', // Point to schema for application tables only
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  migrations: {
    schema: './src/lib/app-schema.ts',
  },
});