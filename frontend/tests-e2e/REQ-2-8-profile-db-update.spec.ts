import { test, expect } from '@playwright/test';

test.describe('REQ-2-8 个人信息数据库落地与登录态联动', () => {
  test('登录态下更新联系方式在页面持久化', async ({ page }) => {
    await page.goto('http://localhost:5173/');

    await page.evaluate(() => {
      window.localStorage.setItem(
        'user',
        JSON.stringify({ token: 'demo-token', username: 'demo_user' }),
      );
      window.localStorage.removeItem('profile');
    });

    await page.goto('http://localhost:5173/profile');

    await expect(page).toHaveURL('http://localhost:5173/profile');
    await expect(page.getByRole('main').getByText('个人中心')).toBeVisible();

    await page.getByRole('button', { name: '编辑联系方式' }).click();

    await page
      .getByText('手机号：')
      .locator('xpath=following-sibling::input[1]')
      .fill('13812345678');
    await page
      .getByText('邮箱：')
      .locator('xpath=following-sibling::input[1]')
      .fill('new_demo@example.com');

    await page.getByRole('button', { name: /保.?存/ }).click();

    await expect(page.getByText('138****5678')).toBeVisible();
    await expect(page.getByText('new_demo@example.com')).toBeVisible();

    await page.reload();

    await expect(page.getByText('138****5678')).toBeVisible();
    await expect(page.getByText('new_demo@example.com')).toBeVisible();
  });
});
