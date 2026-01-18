import { test, expect } from '@playwright/test';

test.describe('REQ-1-7/1-8 数据鲁棒性与交互细节', () => {
  test('搜索无结果时显示暂无车次信息', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    await page.getByPlaceholder('出发地').fill('南极');
    await page.getByPlaceholder('目的地').fill('上海');
    await page.getByRole('button', { name: '查询' }).click();

    await expect(page.getByText('暂无车次信息')).toBeVisible();
  });

  test('点击浮层外部关闭城市选择器', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const fromInput = page.getByPlaceholder('出发地');
    await fromInput.click();

    const popup = page.getByTestId('city-selector-popup');
    await expect(popup).toBeVisible();

    await page.getByText('Railway 12306 仿站 - 单程查询').click();

    await expect(popup).toBeHidden();
  });
});

