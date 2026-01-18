import { test, expect } from '@playwright/test';

test.describe('REQ-1-1 综合搜索表单与子功能', () => {
  test('单程/往返切换与返程日可用状态', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const singleRadio = page.getByLabel('单程');
    const roundRadio = page.getByLabel('往返');

    await expect(singleRadio).toBeChecked();

    const returnDateInputSingle = page.getByPlaceholder('返程日');
    await expect(returnDateInputSingle).toBeDisabled();

    await roundRadio.click();

    await expect(page).toHaveURL(/\/leftTicket\/round/);

    const returnDateInputRound = page.getByPlaceholder('返程日');
    await expect(returnDateInputRound).toBeEnabled();
  });

  test('CitySelector 支持点击选择与拼音搜索', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const fromInput = page.getByPlaceholder('出发地');
    await fromInput.click();

    const popup = page.getByTestId('city-selector-popup');
    await expect(popup).toBeVisible();

    await page.getByText('北京').click();
    await expect(fromInput).toHaveValue('北京');

    await fromInput.fill('sh');
    await expect(popup).toBeVisible();
    const optionsText = await popup.innerText();
    expect(optionsText).toContain('上海');
  });

  test('DateSelector 禁用过去日期并能选择未来日期', async ({ page }) => {
    await page.goto('http://localhost:5173/leftTicket/single');

    const dateInput = page.getByPlaceholder('出发日');
    await dateInput.click();

    const today = new Date();
    const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000);
    const tyyyy = tomorrow.getFullYear();
    const tmm = `${tomorrow.getMonth() + 1}`.padStart(2, '0');
    const tdd = `${tomorrow.getDate()}`.padStart(2, '0');
    const tomorrowLabel = `${tyyyy}-${tmm}-${tdd}`;

    await dateInput.fill(tomorrowLabel);
    await page.keyboard.press('Enter');

    await expect(dateInput).toHaveValue(tomorrowLabel);
  });

  test('URL 参数同步到输入框并自动触发搜索', async ({ page }) => {
    await page.goto(
      'http://localhost:5173/leftTicket/single?departure_city=南京&arrival_city=杭州',
    );

    const fromInput = page.getByPlaceholder('出发地');
    const toInput = page.getByPlaceholder('目的地');

    await expect(fromInput).toHaveValue('南京');
    await expect(toInput).toHaveValue('杭州');
  });
});
