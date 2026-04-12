"""
検証センターの状態を確認するスクリプト。
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

        print("1. 検証センターを確認...")
        await page.goto("https://console.cloud.google.com/auth/verification", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)
        await screenshot(page, "verification")
        print(f"   URL: {page.url}")

        # ページ内のテキストを取得
        text = await page.evaluate("""() => {
            const main = document.querySelector('main') || document.body;
            return main.innerText.substring(0, 2000);
        }""")
        print(f"   ページ内容:\n{text[:1000]}")

        await browser.close()

asyncio.run(main())
