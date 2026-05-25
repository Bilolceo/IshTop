import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import path from "node:path";

type Json = Record<string, any>;

const APP_URL = "http://127.0.0.1:3000";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
const E2E_SEED_FILE = path.join(process.cwd(), "test-results", "e2e-seed.json");

function getSeededSmokeAdmin() {
  try {
    const seed = JSON.parse(readFileSync(E2E_SEED_FILE, "utf8")) as Json;
    const smokeAdmin = seed.smokeAdmin as Json | undefined;
    if (smokeAdmin?.email && smokeAdmin?.password) {
      return { email: String(smokeAdmin.email), password: String(smokeAdmin.password) };
    }
  } catch {
    // Fall through to the legacy admin for externally pre-seeded environments.
  }

  return {
    email: process.env.E2E_ADMIN_EMAIL || "admin@ishtop.uz",
    password: process.env.E2E_ADMIN_PASSWORD || "Admin123!",
  };
}

async function loginAndBuildAuthStorage(request: any, email: string, password: string) {
  let res: any = null;
  for (let attempt = 1; attempt <= 6; attempt++) {
    res = await request.post(`${API_URL}/auth/login`, {
      data: { email, password },
      headers: { "content-type": "application/json" },
    });
    if (res.ok()) break;
    if (res.status() === 429 && attempt < 6) {
      const retryAfter = Number(res.headers()["retry-after"] || "3");
      await new Promise((resolve) => setTimeout(resolve, Math.max(1, retryAfter) * 1000));
      continue;
    }
    break;
  }

  if (!res?.ok()) {
    const status = res?.status?.() ?? "no response";
    const body = res ? await res.text() : "";
    throw new Error(`Login failed for ${email} (${status}): ${body}`);
  }

  const data = (await res.json()) as Json;

  return JSON.stringify({
    state: {
      user: data.user,
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
      isAuthenticated: true,
      hasHydrated: true,
    },
    version: 0,
  });
}

async function applyAuthState(page: any, storageValue: string) {
  await page.addInitScript((value) => {
    if (typeof value === "string") {
      localStorage.setItem("auth-storage", value);
    }
  }, storageValue);
}

test.describe("Smoke Expansion", () => {
  test("admin dashboard loads with seeded admin account", async ({ page, request }) => {
    const admin = getSeededSmokeAdmin();
    const authStorage = await loginAndBuildAuthStorage(request, admin.email, admin.password);
    await applyAuthState(page, authStorage);

    await page.goto(`${APP_URL}/admin`);

    await expect(page).toHaveURL(/\/admin/);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(/Platformani kuzating/i, {
      timeout: 15000,
    });
    await expect(page.getByText(/Foydalanuvchi statistikasi/i)).toBeVisible({ timeout: 15000 });
    await expect(
      page.getByRole("heading", {
        level: 2,
        name: /system health|tizim holati|состояние системы/i,
      })
    ).toBeVisible({
      timeout: 15000,
    });
  });

  test("company job post flow creates and publishes a new job", async ({ page, request }) => {
    const authStorage = await loginAndBuildAuthStorage(request, "acme.hr@example.com", "Company123!");
    await applyAuthState(page, authStorage);

    const uniqueTitle = `E2E QA Engineer ${Date.now()}`;

    await page.goto(`${APP_URL}/company/jobs/new`);

    await expect(page).toHaveURL(/\/company\/jobs\/new/);

    await page.locator("#title").fill(uniqueTitle);
    await page.locator("#location").fill("Tashkent, Uzbekistan");
    await page.getByRole("button", { name: /Keyingi|Next/i }).first().click({ force: true });

    await page.getByPlaceholder(/Lavozim haqida batafsil ma'lumot/i).fill(
      "We are looking for a QA engineer who can write reliable automated tests, collaborate with product teams, and improve release quality."
    );
    await page.getByRole("button", { name: /Keyingi|Next/i }).first().click({ force: true });

    await page.getByPlaceholder(/Nomzodga qo'yiladigan talablar/i).fill(
      "Manual testing, automated testing, test design, bug reporting, regression analysis, API testing."
    );
    await page.getByPlaceholder(/Ko'nikma qo'shish/i).fill("Testing");
    await page.getByRole("button", { name: /Qo'shish|Add/i }).click();
    await page.getByRole("button", { name: /Keyingi|Next/i }).first().click({ force: true });

    await page.getByRole("button", { name: /E'lon qilish|Publish/i }).first().click({ force: true });

    await expect(page).toHaveURL(/\/company\/jobs/);
    await expect(page.getByText(uniqueTitle).first()).toBeVisible({ timeout: 15000 });
  });
});
