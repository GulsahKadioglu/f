import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {

  test('✅ should allow a user to log in successfully and redirect to cases page', async ({ page }) => {
    // Login sayfasına git
    await page.goto('http://localhost:3000/login');

    // Email ve şifreyi doldur
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('testpassword');

    // Login butonuna tıkla
    await page.getByRole('button', { name: /login/i }).click();

    // Redirect bekle → /cases
    await expect(page).toHaveURL('http://localhost:3000/cases');

    // "Case Management" başlığı gözüküyor mu kontrol et
    await expect(page.getByRole('heading', { name: /case management/i })).toBeVisible();
  });

  test('❌ should display an error message with invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    // Yanlış bilgiler doldur
    await page.getByLabel('Email').fill('wrong@example.com');
    await page.getByLabel('Password').fill('wrongpassword');

    // Login denemesi
    await page.getByRole('button', { name: /login/i }).click();

    // Hata mesajı gözüküyor mu kontrol et
    await expect(page.getByText(/login failed/i)).toBeVisible();

    // URL hâlâ login sayfasında mı
    await expect(page).toHaveURL('http://localhost:3000/login');
  });

});

