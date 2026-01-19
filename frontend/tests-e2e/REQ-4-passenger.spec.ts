import { test, expect } from '@playwright/test';

test.describe('Passenger Management', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    page.on('pageerror', err => console.log(`BROWSER ERROR: ${err}`));
    
    // Navigate to passenger page directly
    await page.goto('/user/passengers');
  });

  test('should create, update and delete a passenger', async ({ page }) => {
    // 1. Verify page title
    await expect(page.locator('h2')).toHaveText('常用联系人', { timeout: 10000 });

    // 2. Add Passenger
    // Ant Design adds a space between two Chinese characters in buttons, so we match loosely
    await page.click('button.ant-btn-primary:has-text("加")');
    await expect(page.locator('.ant-modal-title')).toHaveText('添加乘客');

    const randomName = `User-${Math.floor(Math.random() * 10000)}`;
    // Generate valid-looking ID card (18 digits)
    const randomId = `11010119900101${Math.floor(1000 + Math.random() * 9000)}`;
    const randomPhone = `138${Math.floor(10000000 + Math.random() * 90000000)}`;

    // Fill form using placeholders
    await page.getByPlaceholder('请输入姓名').fill(randomName);
    await page.getByPlaceholder('请输入证件号码').fill(randomId);
    await page.getByPlaceholder('请输入手机号').fill(randomPhone);

    // Click OK in Modal
    await page.click('.ant-modal-footer button.ant-btn-primary');

    // Wait for modal to close and table to reload
    await expect(page.locator('.ant-modal')).toBeHidden();
    // Verify the new passenger is in the table
    await expect(page.locator('table')).toContainText(randomName);

    // 3. Edit Passenger
    // Find the row with randomName
    const row = page.locator('tr', { hasText: randomName });
    await row.locator('a:has-text("编辑")').click();

    await expect(page.locator('.ant-modal-title')).toHaveText('编辑乘客');
    const newName = randomName + '-Edited';
    await page.getByPlaceholder('请输入姓名').fill(newName);
    await page.click('.ant-modal-footer button.ant-btn-primary');

    await expect(page.locator('.ant-modal')).toBeHidden();
    await expect(page.locator('table')).toContainText(newName);

    // 4. Delete Passenger
    const rowEdited = page.locator('tr', { hasText: newName });
    await rowEdited.locator('a:has-text("删除")').click();
    
    // Handle Popconfirm
    await expect(page.locator('.ant-popover')).toBeVisible();
    await page.click('.ant-popover button.ant-btn-primary'); // Confirm button

    // Verify deletion
    await expect(page.locator('table')).not.toContainText(newName);
  });
});
