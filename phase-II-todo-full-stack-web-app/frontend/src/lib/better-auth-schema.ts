/**
 * Drizzle schema definitions for Better Auth tables
 * This allows explicit control over table creation using Drizzle Kit
 */

import { pgTable, text, timestamp, boolean } from "drizzle-orm/pg-core";

// User table for Better Auth
export const users = pgTable("user", {
  id: text("id").primaryKey(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("emailVerified").default(false),
  name: text("name"),
  image: text("image"),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Session table for Better Auth
export const sessions = pgTable("session", {
  id: text("id").primaryKey(),
  userId: text("userId").notNull().references(() => users.id),
  expiresAt: timestamp("expiresAt", { mode: 'date' }).notNull(),
  token: text("token").notNull().unique(),
  ipAddress: text("ipAddress"),
  userAgent: text("userAgent"),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});

// Account table for Better Auth
export const accounts = pgTable("account", {
  id: text("id").primaryKey(),
  userId: text("userId").notNull().references(() => users.id),
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

// Verification table for Better Auth
export const verifications = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expiresAt", { mode: 'date' }).notNull(),
  createdAt: timestamp("createdAt", { mode: 'date' }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: 'date' }).defaultNow().notNull(),
});