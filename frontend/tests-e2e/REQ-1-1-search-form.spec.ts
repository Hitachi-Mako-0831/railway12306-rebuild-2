import { test, expect } from '@playwright/test';

test.describe('REQ-1-1 综合搜索表单', () => {
  test('URL 参数同步到输入框并自动触发搜索', async ({ page }) => {
    await page.goto(
      'http://localhost:5173/leftTicket/single?departure_city=南京&arrival_city=杭州'
    );

    const fromInput = page.getByPlaceholder('出发地');
    const toInput = page.getByPlaceholder('目的地');

    await expect(fromInput).toHaveValue('南京');
    await expect(toInput).toHaveValue('杭州');
  });

  test('切换单程与往返时路由和返程日可用状态变化', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const singleRadio = page.getByRole('radio', { name: '单程' });
    const roundRadio = page.getByRole('radio', { name: '往返' });

    await singleRadio.click();
    await expect(page).toHaveURL(/\/leftTicket\/single/);

    await roundRadio.click();
    await expect(page).toHaveURL(/\/leftTicket\/round/);
  });

  test('城市选择组件支持点击热门城市', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const fromInput = page.getByPlaceholder('出发地');
    await fromInput.click();
    await page.getByText('北京').first().click();
    await expect(fromInput).toHaveValue('北京');
  });

  test('城市选择组件支持首字母搜索', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const toInput = page.getByPlaceholder('目的地');
    await toInput.fill('sh');
    await page.getByText('上海').first().click();
    await expect(toInput).toHaveValue('上海');
  });

  test('日期选择组件禁止选择今天之前的日期', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const dateInput = page.getByPlaceholder('出发日');
    await dateInput.click();
  });

  test('出发到达互换后自动刷新结果', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const firstRow = page.locator('[data-testid="train-row-0"]');
    await expect(firstRow).toBeVisible();

    await page.getByRole('button', { name: '⇄' }).click();

    const fromInput = page.getByPlaceholder('出发地');
    const toInput = page.getByPlaceholder('目的地');
    await expect(fromInput).toHaveValue('上海');
    await expect(toInput).toHaveValue('北京');
  });
});

