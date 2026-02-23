import { toNextJsHandler } from "better-auth/next-js";

// Force dynamic rendering to prevent build-time initialization
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// With Neon HTTP driver, ensure transaction completes by potentially
// forcing execution of pending database operations before response
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

  // Add a slight delay to ensure Neon HTTP driver transactions complete
  // This addresses the common issue with serverless functions where the
  // function completes before Neon's HTTP transaction commit is processed
  const response = await handler.POST(request);

  // In serverless environments, wait briefly to ensure transaction is completed
  // before the request lifecycle continues
  if (process.env.NODE_ENV !== 'development') {
    // Only in production where serverless functions are used
    await new Promise(resolve => setTimeout(resolve, 250));
  } else {
    // In development for debugging
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  return response;
}
