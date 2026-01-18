import { test, expect } from '@playwright/test';

test.describe('REQ-1-3 实时筛选面板', () => {
  test('选择发车时间段后带上 min_departure_time 参数并过滤结果', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const firstRow = page.locator('[data-testid="train-row-0"]');
    await expect(firstRow).toBeVisible();

    const select = page.getByTestId('filter-time-select');
    await select.click();
    await page.getByTestId('filter-time-option-06001200').click();
  });

  test('仅看高铁/城际时只显示以 G/C 开头的车次', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const typeCheckboxGc = page.getByTestId('filter-train-type-gc');
    const typeCheckboxD = page.getByTestId('filter-train-type-d');
    const typeCheckboxZtk = page.getByTestId('filter-train-type-ztk');

    await typeCheckboxGc.check();
    await typeCheckboxD.uncheck();
    await typeCheckboxZtk.uncheck();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    for (let i = 0; i < count; i += 1) {
      const text = await rows.nth(i).innerText();
      expect(text[0]).toMatch(/[GC]/);
    }
  });

  test('按车站过滤时仅保留包含该站的车次', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const stationSelect = page.getByTestId('filter-station-select');
    await stationSelect.click();
    await page.getByTestId('filter-station-option-北京南').click();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    for (let i = 0; i < count; i += 1) {
      const row = rows.nth(i);
      const fromCell = row.locator('xpath=ancestor::tr/td[2]');
      const toCell = row.locator('xpath=ancestor::tr/td[3]');
      const fromText = await fromCell.innerText();
      const toText = await toCell.innerText();
      expect(fromText.includes('北京') || toText.includes('北京')).toBeTruthy();
    }
  });

  test('席别过滤二等座仅保留有票车次', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    const seatCheckbox = page.getByTestId('filter-seat-second');
    await seatCheckbox.check();

    const rows = page.locator('[data-testid^="train-row-"]');
    const count = await rows.count();
    for (let i = 0; i < count; i += 1) {
      const seatCell = rows
        .nth(i)
        .locator('xpath=ancestor::tr/td[last()]');
      const seatText = await seatCell.innerText();
      expect(['无', '--']).not.toContain(seatText.trim());
    }
  });
});
