# Portfolio Genius - Playwright Testing

This directory contains end-to-end tests for the Portfolio Genius application using Playwright.

## Setup

1. Install Playwright dependencies:
```bash
npm install
```

2. Install Playwright browsers:
```bash
npx playwright install
```

Or use the setup script:
```bash
chmod +x setup-playwright.sh
./setup-playwright.sh
```

## Running Tests

### Basic test execution:
```bash
npm test
```

### Interactive UI mode:
```bash
npm run test:ui
```

### Run tests with browser visible:
```bash
npm run test:headed
```

### Debug mode:
```bash
npm run test:debug
```

### View test report:
```bash
npm run test:report
```

## Test Structure

- `portfolio-creation.spec.ts` - Tests for portfolio creation functionality

## Test Coverage

The current test suite covers:

### Portfolio Creation Tests
- ✅ Complete portfolio creation flow with authentication
- ✅ Form validation for required fields
- ✅ Cash balance validation (negative values, invalid inputs)
- ✅ Public/private visibility toggle
- ✅ Cancel functionality
- ✅ Error handling for network failures
- ✅ Verification of created portfolio details

### Test Scenarios
1. **Happy Path**: Full portfolio creation with all fields
2. **Validation**: Required field validation
3. **Edge Cases**: Invalid cash balance inputs
4. **User Experience**: Cancel and error handling
5. **Integration**: Portfolio appears in dashboard after creation

## Configuration

The tests are configured to:
- Run against `localhost:3000` (automatically started)
- Test in multiple browsers (Chrome, Firefox, Safari)
- Include mobile viewports
- Capture screenshots on failure
- Record videos on failure
- Generate detailed HTML reports

## Environment

Tests assume:
- Firebase emulators are running (if using local Firebase)
- Next.js app is running on port 3000
- Test user credentials are properly configured

## Adding New Tests

1. Create new `.spec.ts` files in the `tests/` directory
2. Follow the existing patterns for authentication and navigation
3. Use descriptive test names and step-by-step organization
4. Include proper assertions and error handling

## Troubleshooting

### Common Issues

1. **Browser not installed**: Run `npx playwright install`
2. **Port 3000 busy**: Make sure no other app is running on port 3000
3. **Test timeouts**: Increase timeout values in `playwright.config.ts`
4. **Authentication issues**: Check Firebase configuration and test credentials

### Debug Failed Tests

1. Run with `--debug` flag to step through tests
2. Use `--headed` to see browser actions
3. Check screenshots and videos in `test-results/`
4. Review HTML report for detailed failure information 