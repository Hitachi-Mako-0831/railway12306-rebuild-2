import { test, expect } from '@playwright/test';

test.describe('REQ-2-1 用户登录基础流程', () => {
  test('使用演示账号成功登录并跳转首页', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByPlaceholder('用户名/邮箱/手机号').fill('demo_user');
    await page.getByPlaceholder('密码').fill('Password123!');

    await page.getByRole('button', { name: '登录' }).click();

    await expect(page.getByText('首页')).toBeVisible();
  });
});

