import { test, expect } from '@playwright/test';

test.describe('REQ-1-2 15天日期快速切换', () => {
  test('点击第二个日期页签到明天并刷新结果', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const tabs = page.locator('[data-testid="date-tab"]');
    const secondTab = tabs.nth(1);

    const secondDate = await secondTab.getAttribute('data-date');
    await secondTab.click();

    const dateInput = page.getByPlaceholder('出发日');
    if (secondDate) {
      await expect(dateInput).toHaveValue(secondDate);
    } else {
      await expect(dateInput).not.toHaveValue('');
    }

    const firstRow = page.locator('[data-testid="train-row-0"]');
    if (await firstRow.count()) {
      await expect(firstRow).toBeVisible();
    }
  });
});
