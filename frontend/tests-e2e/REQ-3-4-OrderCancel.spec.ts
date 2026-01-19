import { test, expect } from '@playwright/test';

test.describe('REQ-3-4 Order Cancel', () => {
  const mockOrder = {
    id: 12345,
    status: 'pending',
    total_price: 100.0,
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 45 * 60 * 1000).toISOString(),
    train: {
      train_number: 'G1234',
      from_station: { name: '北京' },
      to_station: { name: '上海' },
      departure_time: '10:00:00',
      arrival_time: '14:30:00'
    },
    items: []
  };

  test('should cancel pending order', async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    // 1. Mock Get Order
    await page.route('**/api/v1/orders/12345', async route => {
      await route.fulfill({ json: mockOrder });
    });

    // 2. Mock Cancel Order
    await page.route('**/api/v1/orders/12345/cancel', async route => {
      await route.fulfill({ json: { ...mockOrder, status: 'cancelled' } });
    });

    // Visit Detail Page
    await page.goto('/order/detail/12345');

    // Click Cancel Button
    // Note: Ant Design confirm modal might need handling
    page.on('dialog', dialog => dialog.accept()); // Fallback for native dialogs, but AntD uses DOM
    
    await page.click('button:has-text("取消订单")');

    // Wait for Modal to appear in DOM
    await page.waitForSelector('.ant-modal');

    // Wait for Modal Title by text
    await expect(page.locator('.ant-modal-title')).toHaveText('确认取消订单?');

    // Click OK button (Try finding button inside the modal that contains the text)
    // Or just find the primary button in the whole page (since modal is on top)
    await page.locator('.ant-modal .ant-btn-primary').click();

    // Verify Status Update (Reload or check UI update)
    // The UI should update status to "已取消"
    // Since we mocked the initial load as pending, and we don't auto-reload the whole page but maybe re-fetch or update local state.
    // Let's assume frontend updates local state or re-fetches.
    
    // We can intercept the re-fetch
    await page.route('**/api/v1/orders/12345', async route => {
      await route.fulfill({ json: { ...mockOrder, status: 'cancelled' } });
    });
    
    // Wait for status update
    await expect(page.locator('.order-status')).toContainText('已取消');
  });
});
