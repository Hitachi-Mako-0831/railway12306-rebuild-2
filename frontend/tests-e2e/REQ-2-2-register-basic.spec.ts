import { test, expect } from '@playwright/test';

test.describe('REQ-2-2 用户注册基础流程', () => {
  test('正常注册后跳转到登录页', async ({ page }) => {
    await page.goto('http://localhost:5173/register');

    const suffix = Date.now().toString();
    const username = `testuser_${suffix}`;
    const email = `testuser_${suffix}@example.com`;

    await page.getByPlaceholder('请输入用户名').fill(username);
    await page.getByPlaceholder('请输入密码').fill('abc12345');
    await page.getByPlaceholder('请再次输入密码').fill('abc12345');
    await page.getByPlaceholder('请输入邮箱').fill(email);

    await page.getByText('我已阅读并同意《用户服务条款》和《隐私政策》').click();

    await page.getByRole('button', { name: '下一步' }).click();

    await page.waitForURL('**/login');
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
  });

  test('密码格式错误时显示提示', async ({ page }) => {
    await page.goto('http://localhost:5173/register');

    await page.getByPlaceholder('请输入用户名').fill('weakuser');
    await page.getByPlaceholder('请输入密码').fill('abcdef');
    await page.getByPlaceholder('请再次输入密码').fill('abcdef');
    await page.getByPlaceholder('请输入邮箱').fill('weak@example.com');

    await page.getByText('我已阅读并同意《用户服务条款》和《隐私政策》').click();

    await page.getByRole('button', { name: '下一步' }).click();

    await expect(page.getByText('密码必须包含字母和数字')).toBeVisible();
  });
});
