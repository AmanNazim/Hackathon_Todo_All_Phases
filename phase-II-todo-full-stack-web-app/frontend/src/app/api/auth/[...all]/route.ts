import { toNextJsHandler } from "better-auth/next-js";

// Force dynamic rendering to prevent build-time initialization
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// With Neon HTTP driver, ensure transaction completes by potentially
// forcing execution of pending database operations before response
export async function GET(request: Request) {
  console.log("📞 [API DEBUG] GET request to auth API");
  console.log("📞 [API DEBUG] Request URL:", request.url);
  console.log("📞 [API DEBUG] Request headers:", Object.fromEntries(request.headers.entries()));
  console.log("🔧 [ENV DEBUG] DATABASE_URL in API route:", process.env.DATABASE_URL ? "SET" : "NOT SET");
  if (process.env.DATABASE_URL) {
    console.log("🔧 [ENV DEBUG] DATABASE_URL (masked):", process.env.DATABASE_URL.replace(/\/\/[^:]+:([^@]+)@/, "//***:***@"));
  }

  const { getAuth } = await import("@/lib/auth");
  console.log("📞 [API DEBUG] Importing getAuth function");

  const auth = await getAuth();
  console.log("📞 [API DEBUG] Auth instance retrieved");

  const handler = toNextJsHandler(auth);
  console.log("📞 [API DEBUG] Handler created");

  const response = await handler.GET(request);
  console.log("📞 [API DEBUG] Handler response generated");

  return response;
}

export async function POST(request: Request) {
  console.log("📞 [API DEBUG] POST request to auth API");
  console.log("📞 [API DEBUG] Request URL:", request.url);
  console.log("📞 [API DEBUG] Request method:", request.method);
  console.log("🔧 [ENV DEBUG] DATABASE_URL in POST API route:", process.env.DATABASE_URL ? "SET" : "NOT SET");
  if (process.env.DATABASE_URL) {
    console.log("🔧 [ENV DEBUG] DATABASE_URL (masked):", process.env.DATABASE_URL.replace(/\/\/[^:]+:([^@]+)@/, "//***:***@"));
  }

  // Get the raw body to log it before processing
  const rawBody = await request.text();
  console.log("📞 [API DEBUG] Raw request body:", rawBody);

  // Recreate the request with the body for the handler
  const processedRequest = new Request(request.url, {
    method: request.method,
    headers: request.headers,
    body: rawBody,
  });

  console.log("📞 [API DEBUG] Importing getAuth function");
  const { getAuth } = await import("@/lib/auth");

  console.log("📞 [API DEBUG] Calling getAuth()");
  const auth = await getAuth();
  console.log("📞 [API DEBUG] Auth instance retrieved, calling handler");

  const handler = toNextJsHandler(auth);
  console.log("📞 [API DEBUG] Handler created, calling POST method");

  // Add a slight delay to ensure Neon HTTP driver transactions complete
  // This addresses the common issue with serverless functions where the
  // function completes before Neon's HTTP transaction commit is processed
  const response = await handler.POST(processedRequest);
  console.log("📞 [API DEBUG] Handler response received");

  // Log the response status
  console.log("📞 [API DEBUG] Response status:", response.status);
  console.log("📞 [API DEBUG] Response headers:", Object.fromEntries(response.headers.entries()));

  // In serverless environments, wait briefly to ensure transaction is completed
  // before the request lifecycle continues
  if (process.env.NODE_ENV !== 'development') {
    // Only in production where serverless functions are used
    console.log("⏳ [API DEBUG] Waiting 250ms for transaction completion (production)");
    await new Promise(resolve => setTimeout(resolve, 250));
  } else {
    // In development for debugging
    console.log("⏳ [API DEBUG] Waiting 50ms for transaction completion (development)");
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  console.log("✅ [API DEBUG] POST request completed");
  return response;
}
