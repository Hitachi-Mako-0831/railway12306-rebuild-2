import { test, expect } from '@playwright/test';

test.describe('REQ-1 完整购票查询流程', () => {
  test('在单程查询页输入条件并看到结果', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('北京');
    await page.getByPlaceholder('目的地').fill('上海');

    await page.getByRole('button', { name: '查询' }).click();

    const firstRow = page.locator('[data-testid="train-row-0"]');
    await expect(firstRow).toBeVisible();
  });
});
