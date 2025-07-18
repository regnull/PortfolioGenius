#!/bin/bash

echo "Setting up Playwright for Portfolio Genius testing..."

# Install Playwright
npm install --save-dev @playwright/test

# Install Playwright browsers
npx playwright install

# Install additional dependencies that might be needed
npm install --save-dev @types/node

echo "Playwright setup complete!"
echo ""
echo "IMPORTANT NOTES:"
echo "1. Make sure your Firebase configuration is set up properly"
echo "2. Start your dev server: npm run dev"
echo "3. Ensure port 3000 is available"
echo ""
echo "Run tests with:"
echo "  npx playwright test                    # Run all tests"
echo "  npx playwright test --headed           # See browser actions"
echo "  npx playwright test --debug           # Debug mode"
echo "  npx playwright test --ui              # Interactive UI"
echo "  npx playwright show-report            # View results"
echo ""
echo "If authentication tests fail:"
echo "1. Check Firebase Auth configuration"
echo "2. Run simple form tests: npx playwright test portfolio-creation-simple.spec.js"
echo "3. Check console logs and screenshots in test-results/" 