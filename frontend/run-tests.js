const { spawn } = require('child_process');
const path = require('path');

console.log('Running tests...');

const jestProcess = spawn('npx', ['jest', 'simple.test.js', '--verbose'], {
  cwd: __dirname,
  stdio: 'inherit'
});

jestProcess.on('close', (code) => {
  console.log(`Jest process exited with code ${code}`);
  process.exit(code);
});

jestProcess.on('error', (err) => {
  console.error('Failed to start Jest:', err);
  process.exit(1);
});