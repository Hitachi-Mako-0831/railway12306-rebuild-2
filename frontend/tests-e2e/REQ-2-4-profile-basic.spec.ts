import { test, expect } from '@playwright/test';

test.describe('REQ-2-4 个人信息管理基础展示', () => {
  test('进入个人中心页面可以看到基本信息模块', async ({ page }) => {
    await page.goto('http://localhost:5173/profile');

    await expect(page.getByRole('main').getByText('个人中心')).toBeVisible();
    await expect(page.getByText('基本信息')).toBeVisible();
    await expect(page.getByText('联系方式', { exact: true })).toBeVisible();
    await expect(page.getByText('附加信息')).toBeVisible();
  });
});
