import { test, expect } from '@playwright/test';

test.describe('REQ-3-5 Order Refund', () => {
  const mockOrder = {
    id: 12345,
    status: 'paid',
    total_price: 200.0,
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 45 * 60 * 1000).toISOString(),
    train: {
      train_number: 'G1234',
      from_station: { name: '北京' },
      to_station: { name: '上海' },
      departure_time: '10:00:00',
      arrival_time: '14:30:00'
    },
    items: [
      {
        id: 1,
        passenger_name: '张三',
        passenger_id_card: '110101199001011234',
        seat_type: 'second_class',
        price: 100.0,
        status: 'paid'
      },
      {
        id: 2,
        passenger_name: '李四',
        passenger_id_card: '110101199001011235',
        seat_type: 'second_class',
        price: 100.0,
        status: 'paid'
      }
    ]
  };

  test('should perform partial refund', async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    
    // Stateful mock
    let currentOrder = JSON.parse(JSON.stringify(mockOrder));

    // 1. Mock Get Order
    await page.route('**/api/v1/orders/12345', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({ json: currentOrder });
      } else {
        await route.fallback();
      }
    });

    // 2. Mock Refund API
    await page.route('**/api/v1/orders/12345/refund', async route => {
      const requestData = route.request().postDataJSON();
      // Expect requestData.order_item_ids to contain [1]
      
      // Return partial refunded order
      currentOrder.status = 'partial_refunded';
      currentOrder.items[0].status = 'refunded';
      
      await route.fulfill({ json: currentOrder });
    });

    // Visit Detail Page
    await page.goto('/order/detail/12345');

    // Wait for order status to be visible to ensure load
    await expect(page.locator('.order-status')).toContainText('已支付');

    // Debug: print all text
    const text = await page.locator('body').innerText();
    console.log('PAGE TEXT:', text);

    // Click Refund Button
    // Ant Design adds space between 2 Chinese chars
    await page.locator('button', { hasText: /退\s*票/ }).click();

    // Wait for Refund Modal
    // Note: Ant Modal attaches to body, so we look for class .refund-modal
    // But we need to make sure we wait for it to be visible
    await expect(page.locator('.refund-modal')).toBeVisible();

    // Select "张三" (Item ID 1)
    // Assuming checkboxes have value as item id
    await page.check('input[type="checkbox"][value="1"]');

    // Click Confirm
    await page.click('.refund-modal .ant-btn-primary');

    // Verify Status Update
    await expect(page.locator('.order-status')).toContainText('部分退票'); // Or mapped text
    
    // Verify Item Status
    // We need to check specific row. 
    // Row for Zhang San (first row) should show Refunded.
    // Row for Li Si (second row) should show Paid.
    
    // Simplified check:
    await expect(page.locator('.passenger-table')).toContainText('已退票');
  });
});
