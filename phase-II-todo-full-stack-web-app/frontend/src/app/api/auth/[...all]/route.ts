import { toNextJsHandler } from "better-auth/next-js";
import { getAuth } from "@/lib/auth";

// Force dynamic rendering to prevent build-time initialization
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Get handlers from lazy-initialized auth instance
export const { GET, POST } = toNextJsHandler(getAuth());
