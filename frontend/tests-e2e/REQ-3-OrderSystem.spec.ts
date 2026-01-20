import { test, expect } from '@playwright/test';

async function registerIfNeeded(request: any, username: string) {
  const password = 'OrderE2E123';
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

async function createOrderFor(request: any, username: string, token: string, totalPrice: number) {
  const headers = { Authorization: `Bearer ${token}` };
  const payload = {
    train_id: 1,
    departure_date: '2025-12-30',
    total_price: totalPrice,
    items: [
      {
        passenger_name: username,
        passenger_id_card: '110101199001019999',
        seat_type: 'second_class',
        price: totalPrice,
      },
    ],
  };

  const res = await request.post('/api/v1/orders/', {
    data: payload,
    headers,
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.id as number;
}

async function getToken(request: any, username: string, password: string) {
  const res = await request.post('/api/v1/login', {
    data: { username, password },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  return body.data.access_token as string;
}

test.describe('REQ-3 Order System', () => {
  test('不同用户在订单列表中只能看到各自订单', async ({ page, request }) => {
    const userA = 'order_user_a';
    const userB = 'order_user_b';

    const passA = await registerIfNeeded(request, userA);
    const passB = await registerIfNeeded(request, userB);

    const tokenA = await getToken(request, userA, passA);
    const tokenB = await getToken(request, userB, passB);

    const orderIdA = await createOrderFor(request, userA, tokenA, 123.45);
    const orderIdB = await createOrderFor(request, userB, tokenB, 234.56);

    await loginAndSetStorage(page, request, userA, passA);
    await page.goto('/user/orders');
    await expect(page.locator('.order-page h1')).toHaveText('我的订单');
    await expect(page.locator('table')).toContainText(String(orderIdA));
    const tableTextA = await page.locator('table').innerText();
    expect(tableTextA).not.toContain(String(orderIdB));

    await loginAndSetStorage(page, request, userB, passB);
    await page.goto('/user/orders');
    await expect(page.locator('table')).toContainText(String(orderIdB));
    const rowsB = page.locator('tbody tr');
    const countB = await rowsB.count();
    for (let i = 0; i < countB; i += 1) {
      const idText = await rowsB.nth(i).locator('td').first().innerText();
      expect(idText.trim()).not.toBe(String(orderIdA));
    }
  });

  test('用户无法通过详情页查看他人订单', async ({ page, request }) => {
    const owner = 'order_owner_detail_e2e';
    const other = 'order_other_detail_e2e';

    const passOwner = await registerIfNeeded(request, owner);
    const passOther = await registerIfNeeded(request, other);

    const tokenOwner = await getToken(request, owner, passOwner);

    const orderId = await createOrderFor(request, owner, tokenOwner, 300.0);

    await loginAndSetStorage(page, request, other, passOther);

    await page.route(`**/api/v1/orders/${orderId}`, async route => {
      const res = await route.fetch();
      if (res.status() === 404) {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Order not found' }),
        });
      } else {
        await route.fulfill({ response: res });
      }
    });

    await page.goto(`/order/detail/${orderId}`);

    await expect(page.locator('body')).toContainText('订单不存在');
  });

  test('订单详情页展示车次与站点信息', async ({ page }) => {
    const mockOrder = {
      id: 12345,
      status: 'pending',
      departure_date: '2025-12-30',
      total_price: 200.0,
      items: [],
      train: {
        id: 1,
        train_number: 'G1234',
        from_station: { name: '北京南' },
        to_station: { name: '上海虹桥' },
        departure_time: '10:00:00',
        arrival_time: '14:30:00',
      },
    };

    await page.route('**/api/v1/orders/12345', async route => {
      await route.fulfill({ json: mockOrder });
    });

    await page.goto('/order/detail/12345');

    await expect(page.locator('.train-info')).toContainText('G1234');
    await expect(page.locator('.train-info')).toContainText('2025-12-30');
    await expect(page.locator('.train-info')).toContainText('北京南');
    await expect(page.locator('.train-info')).toContainText('上海虹桥');
    await expect(page.locator('.train-info')).toContainText('10:00');
    await expect(page.locator('.train-info')).toContainText('14:30');
  });
});
