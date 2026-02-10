import { toNextJsHandler } from "better-auth/next-js";

// Force dynamic rendering to prevent build-time initialization
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Lazy import auth only at runtime
async function getAuthHandler() {
  const { auth } = await import("@/lib/auth");
  return toNextJsHandler(auth);
}

export async function GET(request: Request) {
  const handler = await getAuthHandler();
  return handler.GET(request);
}

export async function POST(request: Request) {
  const handler = await getAuthHandler();
  return handler.POST(request);
}
