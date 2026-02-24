/**
 * Debug script to test the registration process step by step with detailed logging
 */
import dotenv from 'dotenv';
dotenv.config();

async function debugRegistration() {
  console.log("🚀 [DEBUG REGISTRATION] Starting registration debug process");
  console.log("🔍 [DEBUG REGISTRATION] Environment variables check:");
  console.log("   - DATABASE_URL exists:", !!process.env.DATABASE_URL);
  console.log("   - BETTER_AUTH_SECRET exists:", !!process.env.BETTER_AUTH_SECRET);
  console.log("   - BETTER_AUTH_URL exists:", !!process.env.BETTER_AUTH_URL);
  console.log("   - NEXT_PUBLIC_APP_URL exists:", !!process.env.NEXT_PUBLIC_APP_URL);

  try {
    console.log("\n📡 [DEBUG REGISTRATION] Attempting to connect to database...");

    // Test database connection directly first
    const { neon } = await import('@neondatabase/serverless');
    const { drizzle } = await import('drizzle-orm/neon-http');

    const sql = neon(process.env.DATABASE_URL);
    console.log("✅ [DEBUG REGISTRATION] Neon client created");

    const db = drizzle(sql);
    console.log("✅ [DEBUG REGISTRATION] Drizzle instance created");

    // Test direct database query
    try {
      const pingResult = await db.execute(`SELECT NOW() as now`);
      console.log("✅ [DEBUG REGISTRATION] Database connection test successful:", pingResult.rows[0]);
    } catch (dbError) {
      console.error("❌ [DEBUG REGISTRATION] Database connection test failed:", dbError.message);
    }

    // Test table existence
    try {
      const tablesResult = await db.execute(`
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND (table_name = 'user' OR table_name = 'session' OR table_name = 'account' OR table_name = 'verification')
        ORDER BY table_name;
      `);
      console.log("📊 [DEBUG REGISTRATION] Better Auth tables found:", tablesResult.rows.map(r => r.table_name));
    } catch (tablesError) {
      console.error("❌ [DEBUG REGISTRATION] Failed to query tables:", tablesError.message);
    }

    // Test user count before registration
    try {
      const userCountBefore = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log("👤 [DEBUG REGISTRATION] Users before test:", userCountBefore.rows[0].count);
    } catch (countError) {
      console.error("❌ [DEBUG REGISTRATION] Failed to count users:", countError.message);
    }

    console.log("\n🔐 [DEBUG REGISTRATION] Attempting to initialize Better Auth...");

    // Now test Better Auth initialization
    const { betterAuth } = await import('better-auth');
    const { drizzleAdapter } = await import('better-auth/adapters/drizzle');

    const auth = betterAuth({
      adapter: drizzleAdapter(db, {
        provider: "pg",
      }),
      emailAndPassword: {
        enabled: true,
        requireEmailVerification: false,
      },
      session: {
        expiresIn: 60 * 60 * 24 * 7,
        updateAge: 60 * 60 * 24,
      },
      plugins: [],
      secret: process.env.BETTER_AUTH_SECRET || "dev-secret-change-in-production",
      baseURL: process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      trustedOrigins: [
        process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      ],
      advanced: {
        useSecureCookies: false,
        defaultCookieAttributes: {
          sameSite: "lax",
        },
      },
      databaseHooks: {
        user: {
          create: {
            before: async ({ data }) => {
              console.log("👤 [DB HOOK DEBUG] BEFORE USER CREATE - Preparing to create user:", data.email);
              return data;
            },
            after: async ({ data }) => {
              console.log("👤 [DB HOOK DEBUG] AFTER USER CREATE - Successfully created user:", data.email);
              console.log("👤 [DB HOOK DEBUG] User ID:", data.id);
            }
          }
        }
      }
    });

    console.log("✅ [DEBUG REGISTRATION] Better Auth instance created successfully");
    console.log("🔑 [DEBUG REGISTRATION] Auth has email/password:", !!auth.$emailPassword);
    console.log("🔑 [DEBUG REGISTRATION] Auth has database:", !!auth.db);

    // Test registration
    const testEmail = `debug-${Date.now()}@example.com`;
    console.log(`\n📝 [DEBUG REGISTRATION] Attempting to register user: ${testEmail}`);

    const mockRequest = new Request('http://localhost:3000/api/auth/sign-up', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: testEmail,
        password: 'TestPassword123!',
        name: 'Debug Test User',
      }),
    });

    try {
      console.log("📡 [DEBUG REGISTRATION] Calling auth.api.signUpEmail...");
      const result = await auth.api.signUpEmail({
        body: {
          email: testEmail,
          password: 'TestPassword123!',
          name: 'Debug Test User',
        },
        request: mockRequest,
      });

      console.log("✅ [DEBUG REGISTRATION] Registration API call successful!");
      console.log("👤 [DEBUG REGISTRATION] Registration result user:", result?.user);

      // Wait a bit to allow for transaction commit
      console.log("⏳ [DEBUG REGISTRATION] Waiting 100ms for potential transaction commit...");
      await new Promise(resolve => setTimeout(resolve, 100));

      // Check if user was created
      const userCountAfter = await db.execute('SELECT COUNT(*) as count FROM "user";');
      console.log("👤 [DEBUG REGISTRATION] Users after registration:", userCountAfter.rows[0].count);

      if (userCountAfter.rows[0].count > 0) {
        console.log("🎉 [DEBUG REGISTRATION] SUCCESS: User appears to have been created!");

        // Get the specific user we just created
        const createdUser = await db.execute(
          'SELECT id, email, name, "createdAt" FROM "user" WHERE email = $1 ORDER BY "createdAt" DESC LIMIT 1',
          [testEmail]
        );

        if (createdUser.rows.length > 0) {
          console.log("👤 [DEBUG REGISTRATION] Created user details:", createdUser.rows[0]);
        } else {
          console.log("❌ [DEBUG REGISTRATION] User not found in database despite count increase");
        }
      } else {
        console.log("❌ [DEBUG REGISTRATION] NO USER FOUND in database after registration!");
      }
    } catch (regError) {
      console.error("❌ [DEBUG REGISTRATION] Registration failed:", regError.message);
      console.error("❌ [DEBUG REGISTRATION] Registration error stack:", regError.stack);
    }
  } catch (error) {
    console.error("❌ [DEBUG REGISTRATION] Overall test failed:", error.message);
    console.error("❌ [DEBUG REGISTRATION] Overall error stack:", error.stack);
  }

  console.log("\n🏁 [DEBUG REGISTRATION] Debug registration process completed");
}

debugRegistration().catch(console.error);