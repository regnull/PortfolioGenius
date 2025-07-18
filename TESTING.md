# Portfolio Creation Testing Guide

This guide provides comprehensive testing instructions for the Portfolio Genius application's portfolio creation functionality.

## Quick Setup

1. **Install Playwright**:
```bash
npm install --save-dev @playwright/test@latest
npx playwright install
```

2. **Run Tests**:
```bash
npx playwright test
```

## Test Files Created

- `tests/portfolio-creation.spec.js` - Main test suite
- `playwright.config.ts` - Configuration file
- `setup-playwright.sh` - Setup script

## Test Coverage

### ✅ Complete Portfolio Creation Flow
- User authentication (signup/login)
- Form interaction and validation
- Portfolio creation with custom cash balance
- Verification of created portfolio

### ✅ Form Validation Tests
- Required field validation
- Cash balance validation (negative/invalid values)
- Field interaction testing

### ✅ User Experience Tests
- Public/private visibility toggle
- Cancel functionality
- Error handling for network failures

### ✅ Integration Tests
- Portfolio appears in dashboard
- Portfolio details page displays correctly
- Cash balance field integration

## Manual Testing Checklist

If you prefer manual testing, follow these steps:

### Setup
1. ✅ Start the development server: `npm run dev`
2. ✅ Navigate to `http://localhost:3000`
3. ✅ Ensure Firebase is configured

### Test Cases

#### 1. Portfolio Creation - Happy Path
- [ ] Navigate to dashboard
- [ ] Click "Create Portfolio"
- [ ] Fill in portfolio name: "My Test Portfolio"
- [ ] Fill in investment goal: "Moderate risk for long-term growth"
- [ ] Fill in description: "Test portfolio description"
- [ ] Fill in cash balance: "15000"
- [ ] Verify all fields are filled correctly
- [ ] Click "Create Portfolio"
- [ ] Verify "Creating..." button state
- [ ] Verify portfolio appears in dashboard list
- [ ] Verify cash balance is displayed as "$15,000"

#### 2. Form Validation
- [ ] Open portfolio creation form
- [ ] Try to submit empty form (button should be disabled)
- [ ] Fill name only (button should stay disabled)
- [ ] Fill name + goal (button should stay disabled)
- [ ] Fill name + goal + cash balance (button should be enabled)

#### 3. Cash Balance Validation
- [ ] Try negative cash balance (-1000)
- [ ] Verify error message appears
- [ ] Try text in cash balance ("invalid")
- [ ] Verify error message appears
- [ ] Try valid cash balance (10000)
- [ ] Verify error message disappears

#### 4. Public/Private Toggle
- [ ] Verify default is private (unchecked)
- [ ] Toggle to public (check box)
- [ ] Toggle back to private (uncheck box)

#### 5. Cancel Functionality
- [ ] Fill some form fields
- [ ] Click "Cancel"
- [ ] Verify form disappears
- [ ] Verify return to dashboard

#### 6. Portfolio Details View
- [ ] Create a portfolio with $25,000 cash balance
- [ ] Click on the portfolio name/card
- [ ] Verify portfolio page loads with correct URL
- [ ] Verify portfolio name in header
- [ ] Verify "Portfolio Information" section
- [ ] Verify cash balance shows "$25,000"

## Running Specific Tests

```bash
# Run all tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test file
npx playwright test portfolio-creation.spec.js

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

## Test Data

The tests use these default values:
- Email: `test@example.com`
- Password: `testpassword123`
- Name: `Test User`
- Portfolio names: `Test Portfolio {timestamp}`

## Troubleshooting

### Common Issues

1. **Port 3000 in use**: Stop other applications using port 3000
2. **Firebase not connected**: Ensure Firebase configuration is correct
3. **Authentication fails**: Check Firebase Auth settings
   - ✅ **FIXED**: Added unique emails per test run to avoid conflicts
   - ✅ **FIXED**: Improved authentication flow with login fallback
   - ✅ **FIXED**: Added comprehensive error detection and debugging
4. **Tests timeout**: Increase timeout values in config
   - ✅ **FIXED**: Increased navigation and action timeouts
   - ✅ **FIXED**: Added longer waits for authentication redirects
5. **Selectors not found**: Verify UI elements exist with correct text/attributes
   - ✅ **FIXED**: Added more specific selectors and form validation
6. **ES Module import errors**: 
   - ✅ **FIXED**: Updated to use ES module imports instead of require()

### Authentication Issues (RESOLVED)

The original authentication error has been fixed with:

1. **Unique email generation**: Each test run uses a unique email to avoid conflicts
2. **Login fallback**: Tests try to login first before attempting signup
3. **Better error detection**: Added comprehensive error message checking
4. **Enhanced debugging**: Screenshots and console logs for troubleshooting
5. **Improved selectors**: More reliable form field targeting
6. **Timeout increases**: Longer waits for Firebase authentication flows

### Debug Steps

1. Run tests with `--headed` to see browser actions
2. Use `--debug` to step through tests
3. Check screenshots in `test-results/` folder
4. Review HTML report with `npx playwright show-report`

## Test Environment

Tests expect:
- Next.js app running on `http://localhost:3000`
- Firebase authentication enabled
- Portfolio creation functionality working
- Dashboard and portfolio detail pages accessible

## Adding New Tests

1. Create new `.spec.js` files in `tests/` directory
2. Use the existing authentication helper
3. Follow the pattern of step-by-step test organization
4. Include proper assertions and error handling

## Integration with CI/CD

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Install dependencies
  run: npm ci

- name: Install Playwright browsers
  run: npx playwright install

- name: Run tests
  run: npx playwright test
```

## Performance Considerations

- Tests run in parallel by default
- Use `--workers=1` for sequential execution
- Consider test isolation and cleanup
- Use proper wait conditions instead of fixed timeouts

## Best Practices

1. **Reliable selectors**: Use data-testid attributes when possible
2. **Explicit waits**: Wait for elements to be visible before interacting
3. **Test isolation**: Each test should be independent
4. **Descriptive names**: Use clear, descriptive test and step names
5. **Error handling**: Include proper error messages and debugging info 