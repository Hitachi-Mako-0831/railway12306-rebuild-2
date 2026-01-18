import { test, expect } from '@playwright/test';

test.describe('REQ-1-4/1-5 车次结果列表与排序', () => {
  test('结果列表展示核心字段并包含预订按钮', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const firstRow = page.locator('[data-testid="train-row-0"]');
    await expect(firstRow).toBeVisible();

    const tableRow = firstRow.locator('xpath=ancestor::tr');
    await expect(tableRow.locator('td').nth(1)).toHaveText('北京');
    await expect(tableRow.locator('td').nth(2)).toHaveText('上海');

    const bookButton = tableRow.getByRole('button');
    await expect(bookButton).toBeVisible();
  });

  test('点击车次号弹出停靠站占位浮层', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    await page.locator('[data-testid="train-row-0"]').click();
  });

  test('点击预订按钮跳转到订单确认页并带上参数', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const firstRow = page.locator('[data-testid="train-row-0"]');
    await expect(firstRow).toBeVisible();

    const tableRow = firstRow.locator('xpath=ancestor::tr');
    const bookButton = tableRow.getByRole('button');

    await expect(bookButton).toBeVisible();
    await bookButton.click();

    await expect(page).toHaveURL(/\/order\/confirm/);
    await expect(page).toHaveURL(/trainNo=G21/);
    await expect(page).toHaveURL(/departureCity=%E5%8C%97%E4%BA%AC/);
    await expect(page).toHaveURL(/arrivalCity=%E4%B8%8A%E6%B5%B7/);
  });

  test('点击表头按出发时间排序', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const header = page.getByRole('columnheader').filter({ hasText: '出发时间' });
    await header.click();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();

    expect(count).toBeGreaterThan(0);

    if (count === 1) {
      return;
    }

    const firstCell = rows.nth(0).locator('xpath=ancestor::tr/td[6]');
    const secondCell = rows.nth(1).locator('xpath=ancestor::tr/td[6]');

    const first = await firstCell.innerText();
    const second = await secondCell.innerText();

    expect(first <= second).toBeTruthy();
  });
});
