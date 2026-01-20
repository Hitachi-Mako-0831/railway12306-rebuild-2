import { test, expect } from '@playwright/test';

test.describe('REQ-0 路由与跨页面集成流', () => {
  test('未登录时通过头部导航完成首页与查询页往返', async ({ page }) => {
    await page.goto('http://localhost:5173/');

    await expect(page.getByText('Railway 12306 仿站').first()).toBeVisible();
    await page.getByRole('menuitem', { name: '车票查询' }).click();

    await expect(page).toHaveURL('http://localhost:5173/leftTicket/single');
    await expect(page.getByText('Railway 12306 仿站 - 单程查询')).toBeVisible();

    await page.getByRole('menuitem', { name: '首页' }).click();
    await expect(page).toHaveURL('http://localhost:5173/');
  });

  test('登录后通过“我的12306”进入个人中心再进入常用联系人', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.getByPlaceholder('用户名/邮箱/手机号').fill('demo_user');
    await page.getByPlaceholder('密码').fill('Password123!');
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('http://localhost:5173/');
    await expect(page.getByText('欢迎，demo_user')).toBeVisible();

    await page.getByText('我的12306').hover();
    await page.getByRole('menuitem', { name: '个人中心' }).click();

    await expect(page).toHaveURL('http://localhost:5173/profile');
    await expect(page.getByRole('main').getByText('个人中心')).toBeVisible();
    await page.goto('http://localhost:5173/');
    await page.click('button:has-text("个人中心")');
    await expect(page).toHaveURL('http://localhost:5173/user/passengers');
    await expect(page.getByRole('heading', { level: 2, name: '常用联系人' })).toBeVisible();
  });
});
