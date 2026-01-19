import { test, expect } from '@playwright/test';

test.describe('REQ-2-2/2-1 注册后登录联动流程', () => {
  test('新注册账号可以使用用户名、邮箱或手机号登录', async ({ page }) => {
    await page.goto('http://localhost:5173/register');

    const suffix = Date.now().toString();
    const username = `flowuser_${suffix}`;
    const email = `flowuser_${suffix}@example.com`;
    const idNumber = `11010119900101${suffix.slice(-4)}`;
    const phone = `138${suffix.slice(-8, -1)}`.padEnd(11, '0');

    await page.getByPlaceholder('请输入用户名').fill(username);
    await page.getByPlaceholder('请输入密码').fill('abc12345');
    await page.getByPlaceholder('请再次输入密码').fill('abc12345');
    await page.getByPlaceholder('请输入邮箱').fill(email);
    await page.getByPlaceholder('请输入姓名').fill('联动测试用户');
    await page.getByPlaceholder('请输入证件号码').fill(idNumber);
    await page.getByPlaceholder('请输入手机号').fill(phone);

    await page
      .getByText('我已阅读并同意《用户服务条款》和《隐私政策》')
      .click();

    await page.getByRole('button', { name: '下一步' }).click();

    await page.waitForURL('**/login');

    const tryLogin = async (identifier: string) => {
      await page.getByPlaceholder('用户名/邮箱/手机号').fill(identifier);
      await page.getByPlaceholder('密码').fill('abc12345');
      await page.getByRole('button', { name: '登录' }).click();

      await expect(page).toHaveURL('http://localhost:5173/');
      await expect(page.getByText(`欢迎，${username}`)).toBeVisible();

      await page.getByText('我的12306').hover();
      await page.getByRole('menuitem', { name: '退出登录' }).click();

      await expect(page.getByText('登录')).toBeVisible();
    };

    await tryLogin(username);
    await page.goto('http://localhost:5173/login');
    await tryLogin(email);
    await page.goto('http://localhost:5173/login');
    await tryLogin(phone);
  });
});
