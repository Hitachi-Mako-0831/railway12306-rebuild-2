import { test, expect } from '@playwright/test';

test.describe('REQ-1-3 实时筛选面板', () => {
  test('时间段快速选择仅保留早间车次', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const select = page.getByTestId('filter-time-select');
    await select.click();
    await page.getByTestId('filter-time-option-06001200').click();

    const cells = page.locator('[data-testid^="train-departure-time-cell-"]');
    const count = await cells.count();
    expect(count).toBeGreaterThan(0);

    const limit = Math.min(count, 3);
    for (let i = 0; i < limit; i += 1) {
      const text = await cells.nth(i).innerText();
      const [hourStr] = text.split(':');
      const hour = parseInt(hourStr, 10);
      expect(hour).toBeGreaterThanOrEqual(6);
      expect(hour).toBeLessThan(12);
    }
  });

  test('车次类型过滤仅保留高铁/城际', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const dCheckbox = page.getByTestId('filter-train-type-d');
    const ztkCheckbox = page.getByTestId('filter-train-type-ztk');

    await dCheckbox.click();
    await ztkCheckbox.click();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i += 1) {
      const text = await rows.nth(i).innerText();
      expect(text[0] === 'G' || text[0] === 'C').toBeTruthy();
    }
  });

  test('动态车站过滤', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const stationSelect = page.getByTestId('filter-station-select');
    await stationSelect.click();
    await page.getByTestId('filter-station-option-北京南').click();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i += 1) {
      const cell = rows.nth(i).locator('xpath=ancestor::tr/td[4]');
      const text = await cell.innerText();
      expect(text).toContain('北京南');
    }
  });

  test('席别过滤仅保留二等座有票车次', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    await page.getByTestId('filter-seat-second').click();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i += 1) {
      const cell = rows.nth(i).locator('xpath=ancestor::tr/td[9]');
      const text = await cell.innerText();
      expect(text !== '无' && text !== '--').toBeTruthy();
    }
  });
});
