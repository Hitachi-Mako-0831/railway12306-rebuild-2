import { test, expect } from '@playwright/test';

test.describe('REQ-2-3 找回密码基础流程', () => {
  test('从登录页进入找回密码并发送重置请求', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByText('忘记密码').click();

    await expect(page).toHaveURL(/\/forgot-password/);

    await page.getByPlaceholder('请输入用户名').fill('demo_user');
    await page.getByPlaceholder('请输入注册邮箱').fill('demo@example.com');

    await page.getByRole('button', { name: '发送重置链接' }).click();

    await page.waitForURL('**/login');
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
  });
});
