import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/lib/auth.ts', // This might need to be adjusted
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});