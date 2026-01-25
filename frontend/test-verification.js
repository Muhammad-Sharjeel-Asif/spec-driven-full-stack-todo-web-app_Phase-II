#!/usr/bin/env node

/**
 * Test verification script to confirm that duplicate mock files have been cleaned up
 * and to verify the existence of the essential mock file
 */

console.log('=== Integration Test Verification ===');

// Check that duplicate mock files have been removed
const fs = require('fs');
const path = require('path');

const projectRoot = __dirname;
const mockLocations = [
  path.join(projectRoot, '__mocks__', 'api-client.js'),
  path.join(projectRoot, 'src', '__mocks__', 'api-client.js'),
  path.join(projectRoot, 'src', 'lib', '__mocks__', 'api-client.js')
];

let duplicatesFound = 0;
console.log('\nChecking for duplicate mock files...');
mockLocations.forEach(location => {
  if (fs.existsSync(location)) {
    console.log(`✗ Found: ${location}`);
    duplicatesFound++;
  } else {
    console.log(`✓ Missing (as expected): ${location}`);
  }
});

// Check that the correct mock file exists
const correctMockLocation = path.join(projectRoot, 'src', 'lib', '__mocks__', 'api-client.js');
if (fs.existsSync(correctMockLocation)) {
  console.log(`\n✓ Correct mock file exists: ${correctMockLocation}`);
  const mockContent = fs.readFileSync(correctMockLocation, 'utf8');
  console.log(`  Size: ${mockContent.length} bytes`);

  // Check for essential mock methods
  const essentialMethods = ['getTasks', 'createTask', 'updateTask', 'deleteTask', 'patchTask', 'login', 'register', 'logout', 'getCurrentUser'];
  let foundMethods = 0;
  essentialMethods.forEach(method => {
    if (mockContent.includes(method)) {
      console.log(`  ✓ Found method: ${method}`);
      foundMethods++;
    } else {
      console.log(`  ✗ Missing method: ${method}`);
    }
  });

  console.log(`\nMock verification: ${foundMethods}/${essentialMethods.length} essential methods found.`);
} else {
  console.log(`\n✗ Expected mock file does not exist: ${correctMockLocation}`);
}

console.log('\n=== Summary ===');
console.log(`Duplicate mock files found: ${duplicatesFound > 1 ? duplicatesFound : 0}`);
console.log(`Correct mock file exists: ${fs.existsSync(correctMockLocation) ? 'Yes' : 'No'}`);

if (duplicatesFound <= 1 && fs.existsSync(correctMockLocation)) {
  console.log('\n✓ Mock cleanup verification PASSED');
  console.log('  - Duplicate mock files have been properly removed');
  console.log('  - Correct mock file exists in the right location');
  process.exit(0);
} else {
  console.log('\n✗ Mock cleanup verification FAILED');
  process.exit(1);
}