import { test, expect } from '@playwright/test';

test.describe('REQ-2 用户登录与顶部导航状态', () => {
  test('未登录时显示登录和注册链接', async ({ page }) => {
    await page.goto('http://localhost:5173/');

    await expect(page.getByText('登录')).toBeVisible();
    await expect(page.getByText('注册')).toBeVisible();
  });

  test('登录成功后跳转首页并显示用户名', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByPlaceholder('用户名/邮箱/手机号').fill('demo_user');
    await page.getByPlaceholder('密码').fill('Password123!');

    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('http://localhost:5173/');

    await expect(page.getByText('欢迎，demo_user')).toBeVisible();
    await expect(page.getByText('我的12306')).toBeVisible();
  });

  test('退出登录后恢复为未登录状态', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByPlaceholder('用户名/邮箱/手机号').fill('demo_user');
    await page.getByPlaceholder('密码').fill('Password123!');

    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('http://localhost:5173/');
    await expect(page.getByText('欢迎，demo_user')).toBeVisible();

    await page.getByText('我的12306').hover();
    await page.getByRole('menuitem', { name: '退出登录' }).click();

    await expect(page).toHaveURL('http://localhost:5173/');
    await expect(page.getByText('登录')).toBeVisible();
    await expect(page.getByText('注册')).toBeVisible();
  });

  test('我的12306下拉菜单可以进入个人中心', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByPlaceholder('用户名/邮箱/手机号').fill('demo_user');
    await page.getByPlaceholder('密码').fill('Password123!');

    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('http://localhost:5173/');

    await page.getByText('我的12306').hover();
    await page.getByRole('menuitem', { name: '个人中心' }).click();

    await expect(page).toHaveURL(/\/profile$/);
  });
});
