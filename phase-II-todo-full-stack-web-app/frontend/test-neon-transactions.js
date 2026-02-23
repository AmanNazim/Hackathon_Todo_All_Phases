/**
 * Test script to verify transaction commit functionality with Neon and Better Auth
 * This test ensures that registration data is properly persisted to the database
 */
import dotenv from 'dotenv';
dotenv.config();

async function testTransactionCommit() {
  console.log('🧪 Testing transaction commit functionality with Neon + Better Auth...');

  try {
    console.log('✅ Starting transaction commit test...');

    // Import the updated auth configuration
    const { auth } = await import('./auth.ts');

    // Check initial user count
    const initialUsers = await auth.$context.adapter.findMany({
      model: 'user',
      where: []
    });
    console.log(`📊 Users before registration: ${initialUsers.length}`);

    const testEmail = `test-${Date.now()}@neon-transaction-test.com`;

    try {
      // Attempt to create a user - this should handle the transaction properly now
      const result = await auth.$context.adapter.create({
        model: 'user',
        data: {
          id: `test-user-${Date.now()}`,
          email: testEmail,
          name: 'Transaction Test User',
          emailVerified: false,
          createdAt: new Date(),
          updatedAt: new Date(),
        }
      });

      console.log(`✅ User creation successful: ${result?.email || result?.id}`);

      // Check if the user now exists in database
      const updatedUsers = await auth.$context.adapter.findMany({
        model: 'user',
        where: [{ field: 'email', operator: 'eq', value: testEmail }]
      });

      console.log(`📊 Users matching test email: ${updatedUsers.length}`);

      if (updatedUsers.length > 0) {
        console.log('🎉 SUCCESS: User was actually persisted to the database!');
        console.log(`📋 User details: ${JSON.stringify(updatedUsers[0], null, 2)}`);
        console.log('✅ Transaction is committing properly with the new configuration');
        return true;
      } else {
        console.log('❌ FAILURE: User creation reported success but data not in database');
        console.log('🔍 This indicates the transaction is not committing properly');
        return false;
      }
    } catch (createError) {
      console.log(`⚠️  Registration failed with error: ${createError.message}`);
      return false;
    }

  } catch (error) {
    console.error('💥 Test failed with error:', error.message);
    console.error('Full error:', error);
    return false;
  }
}

// Run the test
testTransactionCommit()
  .then(success => {
    if (success) {
      console.log('\n✅ TRANSACTION COMMIT TEST PASSED - Data persistence is working!');
    } else {
      console.log('\n❌ TRANSACTION COMMIT TEST FAILED - Data persistence issues remain');
    }
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Test script error:', error);
    process.exit(1);
  });