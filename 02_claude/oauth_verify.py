"""
承認済みドメインの状態とブランディングの下部を確認するスクリプト。
"""
import asyncio
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"


async def screenshot(page, name):
    path = f"/tmp/oauth_{name}.png"
    await page.screenshot(path=path, full_page=True)
    print(f"   screenshot: {path}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("1. ブランディングページを開きます...")
        await page.goto("https://console.cloud.google.com/auth/branding", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)

        # ページ下部にスクロール
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await screenshot(page, "final_branding_bottom")

        # 承認済みドメインの値を確認
        inputs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input[type="text"]'))
                .filter(el => el.offsetParent !== null)
                .map(el => ({
                    id: el.id,
                    value: el.value,
                    placeholder: el.placeholder,
                }));
        }""")
        print("   入力欄:")
        for inp in inputs:
            print(f"   id={inp['id']}: value='{inp['value']}' placeholder='{inp['placeholder']}'")

        # 承認済みドメインの横に検証済みマーク等があるか
        text = await page.evaluate("() => document.body.innerText")
        for line in text.split('\n'):
            line = line.strip()
            if 'ドメイン' in line or 'domain' in line.lower() or '承認' in line or '確認' in line:
                print(f"   >>> {line[:120]}")

        await browser.close()

asyncio.run(main())
