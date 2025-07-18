import { test, expect, type Page } from '@playwright/test';

// Test configuration
const TEST_USER_EMAIL = 'test@example.com';
const TEST_USER_PASSWORD = 'testpassword123';
const TEST_USER_NAME = 'Test User';

// Helper function to format currency (matching the app's formatting)
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

// Helper function to handle authentication
async function authenticateUser(page: Page): Promise<void> {
  // Check if we're already logged in by looking for dashboard content
  try {
    await page.waitForSelector('text=Your Portfolios', { timeout: 3000 });
    // Already logged in, navigate to dashboard
    await page.goto('/dashboard');
    return;
  } catch {
    // Not logged in, proceed with authentication
  }

  // Navigate to signup page
  await page.goto('/signup');
  
  // Fill signup form
  await page.fill('input[type="text"]', TEST_USER_NAME); // Display name
  await page.fill('input[type="email"]', TEST_USER_EMAIL);
  await page.fill('input[type="password"]', TEST_USER_PASSWORD);
  
  // Submit signup form
  await page.click('button[type="submit"]');
  
  // Wait for redirect to dashboard
  await expect(page).toHaveURL(/.*dashboard/);
}

test.describe('Portfolio Creation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should create a new portfolio successfully', async ({ page }) => {
    // Step 1: Authenticate user
    await test.step('Authenticate user', async () => {
      await authenticateUser(page);
    });

    // Step 2: Open portfolio creation form
    await test.step('Open portfolio creation form', async () => {
      await expect(page.locator('text=Your Portfolios')).toBeVisible();
      
      // Click create portfolio button
      await page.click('text=Create Portfolio');
      
      // Verify form is visible
      await expect(page.locator('text=Create New Portfolio')).toBeVisible();
    });

    // Step 3: Fill portfolio creation form
    const portfolioName = `Test Portfolio ${Date.now()}`;
    const portfolioGoal = 'Test investment goal for automated testing - moderate risk with diversified assets';
    const portfolioDescription = 'This is a test portfolio created by Playwright automation';
    const initialCashBalance = '25000';

    await test.step('Fill portfolio creation form', async () => {
      // Fill portfolio name
      await page.fill('input[placeholder="My Investment Portfolio"]', portfolioName);
      
      // Fill investment goal
      await page.fill('textarea[placeholder="Define your investment goal and strategy..."]', portfolioGoal);
      
      // Fill description
      await page.fill('textarea[placeholder="Optional description of your portfolio strategy..."]', portfolioDescription);
      
      // Fill initial cash balance
      await page.fill('input[placeholder="10000"]', initialCashBalance);
      
      // Verify form is filled correctly
      await expect(page.locator('input[placeholder="My Investment Portfolio"]')).toHaveValue(portfolioName);
      await expect(page.locator('textarea[placeholder="Define your investment goal and strategy..."]')).toHaveValue(portfolioGoal);
      await expect(page.locator('textarea[placeholder="Optional description of your portfolio strategy..."]')).toHaveValue(portfolioDescription);
      await expect(page.locator('input[placeholder="10000"]')).toHaveValue(initialCashBalance);
    });

    // Step 4: Submit portfolio creation form
    await test.step('Submit portfolio creation form', async () => {
      // Click create portfolio button
      await page.click('button:has-text("Create Portfolio")');
      
      // Wait for form to be submitted (button should show "Creating...")
      await expect(page.locator('button:has-text("Creating...")')).toBeVisible();
      
      // Wait for form to disappear (successful creation)
      await expect(page.locator('text=Create New Portfolio')).toBeHidden({ timeout: 10000 });
    });

    // Step 5: Verify portfolio was created
    await test.step('Verify portfolio was created', async () => {
      // Check if portfolio appears in the list
      await expect(page.locator(`text=${portfolioName}`)).toBeVisible({ timeout: 5000 });
      
      // Verify portfolio details are displayed
      await expect(page.locator('text=Private')).toBeVisible(); // Default visibility
      await expect(page.locator(`text=${formatCurrency(parseFloat(initialCashBalance))}`)).toBeVisible();
    });

    // Step 6: Click on portfolio to view details
    await test.step('View portfolio details', async () => {
      // Click on the portfolio name/card
      await page.click(`text=${portfolioName}`);
      
      // Wait for portfolio page to load
      await expect(page).toHaveURL(/.*portfolio\/[^\/]+/);
      
      // Verify portfolio information is displayed
      await expect(page.locator('h1')).toContainText(portfolioName);
      await expect(page.locator('text=Portfolio Information')).toBeVisible();
      await expect(page.locator(`text=${formatCurrency(parseFloat(initialCashBalance))}`)).toBeVisible();
    });
  });

  test('should validate required fields', async ({ page }) => {
    // Authenticate user
    await authenticateUser(page);
    
    // Open portfolio creation form
    await page.click('text=Create Portfolio');
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();

    // Try to submit without filling required fields
    await page.click('button:has-text("Create Portfolio")');
    
    // Button should be disabled
    await expect(page.locator('button:has-text("Create Portfolio")[disabled]')).toBeVisible();
    
    // Fill only name
    await page.fill('input[placeholder="My Investment Portfolio"]', 'Test Portfolio');
    
    // Button should still be disabled (missing goal and cash balance)
    await expect(page.locator('button:has-text("Create Portfolio")[disabled]')).toBeVisible();
    
    // Fill goal but not cash balance
    await page.fill('textarea[placeholder="Define your investment goal and strategy..."]', 'Test goal');
    
    // Button should still be disabled (missing cash balance)
    await expect(page.locator('button:has-text("Create Portfolio")[disabled]')).toBeVisible();
    
    // Fill cash balance
    await page.fill('input[placeholder="10000"]', '5000');
    
    // Button should now be enabled
    await expect(page.locator('button:has-text("Create Portfolio"):not([disabled])')).toBeVisible();
  });

  test('should validate cash balance input', async ({ page }) => {
    // Authenticate user
    await authenticateUser(page);
    
    // Open portfolio creation form
    await page.click('text=Create Portfolio');
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();

    // Fill required fields
    await page.fill('input[placeholder="My Investment Portfolio"]', 'Test Portfolio');
    await page.fill('textarea[placeholder="Define your investment goal and strategy..."]', 'Test goal');
    
    // Test negative cash balance
    await page.fill('input[placeholder="10000"]', '-1000');
    await page.click('button:has-text("Create Portfolio")');
    
    // Should show error message
    await expect(page.locator('text=Initial cash balance must be a non-negative number')).toBeVisible();
    
    // Test invalid cash balance (letters)
    await page.fill('input[placeholder="10000"]', 'invalid');
    await page.click('button:has-text("Create Portfolio")');
    
    // Should show error message
    await expect(page.locator('text=Initial cash balance must be a non-negative number')).toBeVisible();
    
    // Test valid cash balance
    await page.fill('input[placeholder="10000"]', '15000');
    await page.click('button:has-text("Create Portfolio")');
    
    // Should not show error and form should submit
    await expect(page.locator('text=Initial cash balance must be a non-negative number')).toBeHidden();
  });

  test('should toggle public/private visibility', async ({ page }) => {
    // Authenticate user
    await authenticateUser(page);
    
    // Open portfolio creation form
    await page.click('text=Create Portfolio');
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();

    // Check initial state (should be private by default)
    const publicCheckbox = page.locator('input[type="checkbox"]').first();
    await expect(publicCheckbox).not.toBeChecked();
    
    // Toggle to public
    await publicCheckbox.check();
    await expect(publicCheckbox).toBeChecked();
    
    // Toggle back to private
    await publicCheckbox.uncheck();
    await expect(publicCheckbox).not.toBeChecked();
  });

  test('should cancel portfolio creation', async ({ page }) => {
    // Authenticate user
    await authenticateUser(page);
    
    // Open portfolio creation form
    await page.click('text=Create Portfolio');
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();

    // Fill some fields
    await page.fill('input[placeholder="My Investment Portfolio"]', 'Test Portfolio');
    await page.fill('textarea[placeholder="Define your investment goal and strategy..."]', 'Test goal');
    
    // Click cancel
    await page.click('button:has-text("Cancel")');
    
    // Form should be hidden
    await expect(page.locator('text=Create New Portfolio')).toBeHidden();
    
    // Should be back to dashboard
    await expect(page.locator('text=Your Portfolios')).toBeVisible();
  });

  test('should handle form submission errors gracefully', async ({ page }) => {
    // Mock network error
    await page.route('**/portfolios', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    // Authenticate user
    await authenticateUser(page);
    
    // Open portfolio creation form
    await page.click('text=Create Portfolio');
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();

    // Fill form
    await page.fill('input[placeholder="My Investment Portfolio"]', 'Test Portfolio');
    await page.fill('textarea[placeholder="Define your investment goal and strategy..."]', 'Test goal');
    await page.fill('input[placeholder="10000"]', '10000');
    
    // Submit form
    await page.click('button:has-text("Create Portfolio")');
    
    // Should show error message
    await expect(page.locator('text=Failed to create portfolio')).toBeVisible();
    
    // Form should still be visible (not dismissed)
    await expect(page.locator('text=Create New Portfolio')).toBeVisible();
  });
}); 