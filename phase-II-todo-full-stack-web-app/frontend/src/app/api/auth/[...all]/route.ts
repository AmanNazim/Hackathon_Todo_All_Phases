import { toNextJsHandler } from "better-auth/next-js";

// Force dynamic rendering to prevent build-time initialization
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Lazy handlers - getAuth() is only called when request actually comes in
export async function GET(request: Request) {
  const { getAuth } = await import("@/lib/auth");
  const auth = await getAuth();
  const handler = toNextJsHandler(auth);
  return handler.GET(request);
}

export async function POST(request: Request) {
  const { getAuth } = await import("@/lib/auth");
  const auth = await getAuth();
  const handler = toNextJsHandler(auth);
  return handler.POST(request);
}
