/**
 * Schema specifically for Better Auth tables
 * Better Auth has its own internal schema, but we need to make sure
 * the drizzle instance knows about the table structure
 */
import { pgTable, text, timestamp, boolean, pgEnum } from "drizzle-orm/pg-core";

// User table - matching Better Auth's expected structure
export const users = pgTable("user", {
  id: text("id").primaryKey(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("emailVerified").default(false),
  name: text("name"),
  image: text("image"),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Session table - matching Better Auth's expected structure
export const sessions = pgTable("session", {
  id: text("id").primaryKey(),
  userId: text("userId").notNull(),
  expiresAt: timestamp("expiresAt", { mode: 'date' }).notNull(),
  token: text("token").notNull().unique(),
  ipAddress: text("ipAddress"),
  userAgent: text("userAgent"),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Account table - matching Better Auth's expected structure
export const accounts = pgTable("account", {
  id: text("id").primaryKey(),
  userId: text("userId").notNull(),
  accountId: text("accountId").notNull(),
  providerId: text("providerId").notNull(),
  accessToken: text("accessToken"),
  refreshToken: text("refreshToken"),
  idToken: text("idToken"),
  expiresAt: timestamp("expiresAt", { mode: 'date' }),
  password: text("password"),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Verification table - matching Better Auth's expected structure
export const verifications = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expiresAt", { mode: 'date' }).notNull(),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Export all schema for use with drizzle
export const baSchema = {
  users,
  sessions,
  accounts,
  verifications
};