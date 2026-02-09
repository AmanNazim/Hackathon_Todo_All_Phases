import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  // Better Auth will handle token storage and management automatically
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
