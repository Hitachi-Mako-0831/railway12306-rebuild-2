import { test, expect } from '@playwright/test';

test.describe('REQ-3-2 Order Detail Page', () => {
  const mockOrder = {
    id: 12345,
    train_id: 1,
    train: { 
      train_number: 'G1234',
      from_station: { name: '北京南' },
      to_station: { name: '上海虹桥' },
      departure_time: '10:00:00',
      arrival_time: '14:30:00'
    },
    status: 'pending',
    total_price: 553.0,
    created_at: '2025-12-30T09:00:00',
    expires_at: '2025-12-30T09:45:00',
    items: [
      {
        id: 1,
        passenger_name: '张三',
        passenger_id_card: '110101199001011234',
        seat_type: 'second_class',
        price: 553.0,
        seat_number: '05车12A'
      }
    ]
  };

  test('should display order details correctly', async ({ page }) => {
    // Mock API
    await page.route('**/api/v1/orders/12345', async route => {
      await route.fulfill({ json: mockOrder });
    });

    // Visit page
    await page.goto('/order/detail/12345');

    // 1. Verify Status Bar (REQ-3-2-2)
    await expect(page.locator('.order-status')).toContainText('待支付');
    await expect(page.locator('.order-no')).toContainText('12345');

    // 2. Verify Train Info (REQ-3-2-3)
    await expect(page.locator('.train-info')).toContainText('G1234');
    await expect(page.locator('.train-info')).toContainText('北京南');
    
    // 3. Verify Passenger List (REQ-3-2-4)
    await expect(page.locator('.passenger-table')).toContainText('张三');
    await expect(page.locator('.passenger-table')).toContainText('二等座');
    await expect(page.locator('.passenger-table')).toContainText('553');

    // 4. Verify Price (REQ-3-2-5)
    await expect(page.locator('.total-price')).toContainText('553');
  });
});
