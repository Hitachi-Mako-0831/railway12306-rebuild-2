import { test, expect } from '@playwright/test';

test.describe('REQ-3-3 Order Pay Page', () => {
  const mockOrder = {
    id: 12345,
    status: 'pending',
    total_price: 100.0,
    created_at: new Date().toISOString(), // Just created
    expires_at: new Date(Date.now() + 45 * 60 * 1000).toISOString(), // +45 mins
    train: {
      train_number: 'G1234',
      from_station: { name: '北京' },
      to_station: { name: '上海' },
      departure_time: '10:00:00',
      arrival_time: '14:30:00'
    },
    items: []
  };

  test('should display payment info and submit payment', async ({ page }) => {
    // 1. Mock Get Order
    await page.route('**/api/v1/orders/12345', async route => {
      await route.fulfill({ json: mockOrder });
    });

    // 2. Mock Pay Order
    await page.route('**/api/v1/orders/12345/pay', async route => {
      await route.fulfill({ json: { ...mockOrder, status: 'paid' } });
    });

    // Visit Pay Page
    await page.goto('/order/pay/12345');

    // Verify Amount
    await expect(page.locator('.pay-amount')).toContainText('100');

    // Verify Countdown (rough check if it exists)
    await expect(page.locator('.countdown')).toBeVisible();

    // Select Payment Method (Optional, usually default is selected)
    // await page.click('text=支付宝');

    // Click Pay
    await page.click('button:has-text("立即支付")');

    // Verify Redirection to Success Page
    await expect(page).toHaveURL(/\/order\/success\?orderId=12345/);
    
    // Verify Success Message
    await expect(page.locator('.success-message')).toContainText('支付成功');
  });
});
