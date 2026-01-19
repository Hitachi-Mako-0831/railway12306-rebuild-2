import { test, expect } from '@playwright/test';

test.describe('REQ-3-1 Order Confirm Page', () => {
  test('should verify train info and submit order', async ({ page }) => {
    // 1. Simulate navigation from search results
    // We assume the URL contains necessary query params as defined in OrderConfirm.vue
    const queryParams = new URLSearchParams({
      trainId: '1',
      trainNo: 'G1234',
      departureCity: '北京',
      arrivalCity: '上海',
      travelDate: '2025-12-30',
      fromStation: '北京南',
      toStation: '上海虹桥',
      departureTime: '10:00',
      arrivalTime: '14:30',
      duration: '270'
    }).toString();

    await page.goto(`/order/confirm?${queryParams}`);

    // 2. Verify Train Info (REQ-3-1-1)
    // Expect card title or specific element to contain train number
    await expect(page.locator('.train-info')).toContainText('G1234');
    await expect(page.locator('.train-info')).toContainText('2025-12-30');

    // 3. Select Passenger (REQ-3-1-2)
    // Assume there is a list of common passengers or a button to add one
    // For this test, we might need to mock the API response for passengers if it's dynamic
    // Or we manually input one if the UI supports "Add Passenger"
    
    // Check if passenger list is visible
    const passengerCheckbox = page.locator('.passenger-item').first();
    // If no passengers, we might need to mock API. 
    // For now, let's assume we can see at least one mock passenger or add one.
    
    // NOTE: Since backend might not have passengers, UI should handle empty state or we inject mock via route interception.
    // We will intercept the passengers API call.
    await page.route('**/api/v1/passengers/', async route => {
      const json = [
        { id: 1, name: '张三', type: 'adult', id_card: '110101199001011234' }
      ];
      await route.fulfill({ json });
    });
    
    // Reload to trigger API call
    await page.reload();
    
    // Select "张三"
    await page.locator('text=张三').click();

    // 4. Verify Seat Selection Row appears (REQ-3-1-3, REQ-3-1-4)
    await expect(page.locator('.ticket-row')).toBeVisible();
    await expect(page.locator('.ticket-row')).toContainText('张三');
    
    // Select Seat Type (e.g., Second Class)
    // Assuming default is set, or we select it.
    
    // 5. Submit Order (REQ-3-1-5)
    await page.locator('button:has-text("提交订单")').click();
    
    // 6. Expect navigation to Order Success or Pay page
    // Or a success message
    // Ideally it redirects to /user/orders or /order/pay/:id
    await expect(page).toHaveURL(/\/order\/pay\/\d+/);
  });

  test('should show error if no passenger selected', async ({ page }) => {
    const queryParams = new URLSearchParams({
      trainNo: 'G1234',
      travelDate: '2025-12-30'
    }).toString();
    await page.goto(`/order/confirm?${queryParams}`);
    
    await page.locator('button:has-text("提交订单")').click();
    
    // Expect error message
    await expect(page.locator('.ant-message-notice')).toContainText('请至少选择一位乘客');
  });
});
