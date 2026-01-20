import { test, expect } from '@playwright/test';

function generateValidId() {
    const addr = "110101";
    const year = 1990 + Math.floor(Math.random() * 10);
    const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
    const day = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
    const birth = `${year}${month}${day}`;
    const seq = String(Math.floor(Math.random() * 999)).padStart(3, '0');
    const body = addr + birth + seq;
    const factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
    const checksumMap = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
    const total = body.split('').reduce((acc, val, idx) => acc + parseInt(val) * factors[idx], 0);
    const checksum = checksumMap[total % 11];
    return body + checksum;
}

test.describe('Passenger Management', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    page.on('pageerror', err => console.log(`BROWSER ERROR: ${err}`));
  });

  test('should navigate from home to passenger page', async ({ page }) => {
    await page.goto('/');
    // Wait for button to be interactive
    await expect(page.locator('button:has-text("个人中心")')).toBeVisible();
    await page.click('button:has-text("个人中心")');
    await expect(page).toHaveURL(/\/user\/passengers/);
    await expect(page.locator('h2')).toHaveText('常用联系人');
  });

  test('should create, search, update and delete a passenger', async ({ page }) => {
    await page.goto('/user/passengers');
    await expect(page.locator('h2')).toHaveText('常用联系人', { timeout: 10000 });

    // 1. Add Passenger
    // Use a more specific selector based on structure
    const addButton = page.locator('.header button'); 
    await expect(addButton).toBeVisible();
    // Ant Design adds space between two Chinese characters
    await expect(addButton).toHaveText(/添\s?加/);
    await addButton.click();
    await expect(page.locator('.ant-modal-title')).toHaveText('添加乘客');

    const randomName = `UserTest`;
    const randomId = generateValidId();
    const randomPhone = `138${Math.floor(10000000 + Math.random() * 90000000)}`;

    await page.getByPlaceholder('请输入姓名').fill(randomName);
    await page.getByPlaceholder('请输入证件号码').fill(randomId);
    await page.getByPlaceholder('请输入手机号').fill(randomPhone);

    await page.click('.ant-modal-footer button.ant-btn-primary');
    await expect(page.locator('.ant-modal')).toBeHidden();
    
    // Wait for table update
    await expect(page.locator('table')).toContainText(randomName);

    // 2. Search Passenger (REQ-4-1-1)
    await page.getByPlaceholder('输入乘客姓名搜索').fill(randomName);
    await page.getByPlaceholder('输入乘客姓名搜索').press('Enter');
    
    // Verify search result
    await expect(page.locator('table')).toContainText(randomName);
    // Ensure we see exactly 1 row (plus header) or at least the result
    const rows = page.locator('tbody tr');
    await expect(rows).toHaveCount(1);
    
    // Clear search
    await page.getByPlaceholder('输入乘客姓名搜索').fill('');
    await page.getByPlaceholder('输入乘客姓名搜索').press('Enter');
    // await expect(rows.count()).resolves.toBeGreaterThan(0);

    // 3. Edit Passenger
    // We need to find the row specifically for this user
    const row = page.locator('tr', { hasText: randomName }).first();
    await row.locator('a:has-text("编辑")').click();

    await expect(page.locator('.ant-modal-title')).toHaveText('编辑乘客');
    const newName = 'UserEdited';
    await page.getByPlaceholder('请输入姓名').fill(newName);
    await page.click('.ant-modal-footer button.ant-btn-primary');

    await expect(page.locator('.ant-modal')).toBeHidden();
    
    // Search again for new name
    await page.getByPlaceholder('输入乘客姓名搜索').fill(newName);
    await page.getByPlaceholder('输入乘客姓名搜索').press('Enter');
    await expect(page.locator('table')).toContainText(newName);

    // 4. Delete Passenger
    const rowEdited = page.locator('tr', { hasText: newName }).first();
    await rowEdited.locator('a:has-text("删除")').click();
    
    await expect(page.locator('.ant-popover')).toBeVisible();
    await page.click('.ant-popover button.ant-btn-primary'); // Confirm button

    // Wait for deletion
    await expect(page.locator('table')).not.toContainText(newName);
  });

  test('should prevent duplicate passenger', async ({ page }) => {
    await page.goto('/user/passengers');
    await expect(page.locator('h2')).toHaveText('常用联系人', { timeout: 10000 });
    
    const randomName = `DupUser`;
    const randomId = generateValidId();
    const randomPhone = `138${Math.floor(10000000 + Math.random() * 90000000)}`;

    // Add first time
    const addButton = page.locator('.header button');
    await expect(addButton).toBeVisible();
    await addButton.click();
    await page.getByPlaceholder('请输入姓名').fill(randomName);
    await page.getByPlaceholder('请输入证件号码').fill(randomId);
    await page.getByPlaceholder('请输入手机号').fill(randomPhone);
    await page.click('.ant-modal-footer button.ant-btn-primary');
    await expect(page.locator('.ant-modal')).toBeHidden();

    // Add second time with same ID
    await addButton.click();
    await page.getByPlaceholder('请输入姓名').fill(randomName + '2');
    await page.getByPlaceholder('请输入证件号码').fill(randomId); // Same ID
    await page.getByPlaceholder('请输入手机号').fill(randomPhone);
    await page.click('.ant-modal-footer button.ant-btn-primary');

    // Expect error message
    await expect(page.locator('.ant-message-notice-content')).toBeVisible();
    
    // Cleanup
    await page.click('.ant-modal-close');
    await expect(page.locator('.ant-modal')).toBeHidden();
    
    const row = page.locator('tr', { hasText: randomName }).first();
    await row.locator('a:has-text("删除")').click();
    await page.click('.ant-popover button.ant-btn-primary');
  });

  test('should protect default passenger (REQ-4-3)', async ({ page }) => {
    const username = `self_passenger_user`;
    const password = `SelfPass1234`;

    const registerResponse = await page.request.post('/api/v1/register', {
      data: {
        username,
        password,
        confirm_password: password,
        email: 'self_passenger_user@example.com',
        real_name: '本人乘车人',
        id_type: 'id_card',
        id_number: generateValidId(),
        phone: '13800008888',
        user_type: 'adult',
      },
    });
    expect(registerResponse.ok()).toBeTruthy();

    const loginResponse = await page.request.post('/api/v1/login', {
      data: {
        username,
        password,
      },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const body = await loginResponse.json();
    const token = body.data.access_token;

    await page.goto('/login');
    await page.getByPlaceholder('用户名/邮箱/手机号').fill(username);
    await page.getByPlaceholder('密码').fill(password);
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('/');

    await page.goto('/user/passengers');
    await expect(page.locator('h2')).toHaveText('常用联系人', { timeout: 10000 });

    // Verify Blue Tag "本人"
    const row = page.locator('tr', { hasText: '本人乘车人' }).first();
    await expect(row.locator('.ant-tag-blue')).toHaveText('本人');
    
    // Verify Delete button is NOT present
    await expect(row.locator('a:has-text("删除")')).not.toBeVisible();

    // Verify Edit restrictions
    await row.locator('a:has-text("编辑")').click();
    await expect(page.locator('.ant-modal-title')).toHaveText('编辑乘客');
    
    // Name and ID Card should be disabled
    const nameInput = page.getByPlaceholder('请输入姓名');
    await expect(nameInput).toBeDisabled();
    
    const idInput = page.getByPlaceholder('请输入证件号码');
    await expect(idInput).toBeDisabled();
    
    // Phone should be editable
    const phoneInput = page.getByPlaceholder('请输入手机号');
    await expect(phoneInput).toBeEditable();
    
    await page.click('.ant-modal-close');
  });
});
