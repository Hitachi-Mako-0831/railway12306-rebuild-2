import { test, expect } from '@playwright/test';

async function registerIfNeeded(request: any, username: string) {
  const password = 'OrderConfirm123';
  const payload = {
    username,
    password,
    confirm_password: password,
    email: `${username}@example.com`,
    real_name: '订单用户',
    id_type: 'id_card',
    id_number: '11010119900101' + Math.floor(Math.random() * 9000 + 1000),
    phone: '138' + Math.floor(10000000 + Math.random() * 90000000),
    user_type: 'adult',
  };

  const res = await request.post('/api/v1/register', { data: payload });
  if (!res.ok() && res.status() !== 400) {
    throw new Error('register failed');
  }

  return password;
}

async function loginAndSetStorage(page: any, request: any, username: string, password: string) {
  const loginRes = await request.post('/api/v1/login', {
    data: { username, password },
  });
  expect(loginRes.ok()).toBeTruthy();
  const body = await loginRes.json();
  const token = body.data.access_token;

  await page.goto('/');
  await page.evaluate(
    ([t, u]: [string, string]) => {
      window.localStorage.setItem('user', JSON.stringify({ token: t, username: u }));
    },
    [token, username],
  );
}

test.describe('REQ-3-1 Order Confirm Page', () => {
  test('should sync departure and arrival time from search result', async ({ page, request }) => {
    const username = 'order_confirm_time_user';
    const password = await registerIfNeeded(request, username);
    await loginAndSetStorage(page, request, username, password);

    await page.route('**/api/v1/trains/search', async route => {
      const json = {
        code: 200,
        message: 'ok',
        data: [
          {
            train_number: 'G21',
            departure_city: '北京',
            arrival_city: '上海',
            departure_time: '08:00',
            arrival_time: '12:30',
            duration_minutes: 270,
            train_type: 'G',
            from_station: '北京南',
            to_station: '上海虹桥',
            seat_second_class: '有',
          },
        ],
      };
      await route.fulfill({ json });
    });

    await page.route('**/api/v1/passengers/', async route => {
      const json = [{ id: 1, name: '张三', type: 'adult', id_card: '110101199001011234' }];
      await route.fulfill({ json });
    });

    await page.route('**/api/v1/orders/', async route => {
      const body = route.request().postDataJSON();
      expect(body.departure_date).toBe('2025-12-30');
      await route.fulfill({ json: { id: 999, total_price: body.total_price, items: body.items } });
    });

    await page.goto('/leftTicket/single?departure_city=北京&arrival_city=上海&travel_date=2025-12-30');

    await expect(page.locator('text=G21')).toBeVisible();

    await page.getByRole('button', { name: '预 订' }).first().click();

    await expect(page).toHaveURL(/\/order\/confirm/);

    await expect(page.locator('.train-info')).toContainText('08:00');
    await expect(page.locator('.train-info')).toContainText('12:30');

    await expect(page.locator('text=张三')).toBeVisible();
    await page.locator('text=张三').click();
    await expect(page.locator('.ticket-row')).toBeVisible();

    await page.locator('button:has-text("提交订单")').click();

    await expect(page).toHaveURL('/order/pay/999');
  });

  test('should verify train info and submit order', async ({ page, request }) => {
    const username = 'order_confirm_user';
    const password = await registerIfNeeded(request, username);
    await loginAndSetStorage(page, request, username, password);

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

  test('should redirect to login when submit without auth', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      window.localStorage.clear();
    });

    await page.route('**/api/v1/passengers/', async route => {
      const json = [
        { id: 1, name: '张三', type: 'adult', id_card: '110101199001011234' }
      ];
      await route.fulfill({ json });
    });

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
    await page.locator('text=张三').click();
    await expect(page.locator('.ticket-row')).toBeVisible();
    await page.locator('button:has-text("提交订单")').click();

    await expect(page.locator('.ant-message-notice')).toContainText('请先登录后再提交订单');
  });

  test('should show backend validation error message instead of object', async ({ page, request }) => {
    const username = 'order_confirm_validation_user';
    const password = await registerIfNeeded(request, username);
    await loginAndSetStorage(page, request, username, password);

    await page.route('**/api/v1/passengers/', async route => {
      const json = [
        { id: 1, name: '张三', type: 'adult', id_card: '110101199001011234' }
      ];
      await route.fulfill({ json });
    });

    await page.route('**/api/v1/orders/', async route => {
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [
            { msg: '测试验证错误', type: 'value_error' },
          ],
        }),
      });
    });

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
    await page.locator('text=张三').click();
    await expect(page.locator('.ticket-row')).toBeVisible();
    await page.locator('button:has-text("提交订单")').click();

    await expect(page.locator('.ant-message-notice')).toContainText('测试验证错误');
  });
});
