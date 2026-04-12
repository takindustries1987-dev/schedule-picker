"""
Google Cloud Console OAuth同意画面の設定を自動化するスクリプト。
"""
import asyncio
from playwright.async_api import async_playwright

CDP_URL = "http://localhost:9222"

APP_NAME = "スケジュールピッカー"
HOMEPAGE_URL = "https://takindustries1987-dev.github.io/schedule-picker/"
PRIVACY_URL = "https://takindustries1987-dev.github.io/schedule-picker/privacy.html"


async def screenshot(page, name):
    path = f"/tmp/oauth_{name}.png"
    await page.screenshot(path=path, full_page=True)
    print(f"   screenshot: {path}")
    return path


async def wait_for_input(page, input_id, timeout=20):
    """Material UI inputが表示されるまで待機"""
    for _ in range(timeout):
        exists = await page.evaluate(f"!!document.getElementById('{input_id}')")
        if exists:
            return True
        await asyncio.sleep(1)
    return False


async def fill_input(page, input_id, value):
    """Material UIのinputに値を入力"""
    await page.evaluate(f"""() => {{
        const el = document.getElementById('{input_id}');
        el.focus();
        el.value = '';
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }}""")
    await asyncio.sleep(0.3)
    await page.fill(f"#{input_id}", value)
    await asyncio.sleep(0.3)
    await page.keyboard.press("Tab")
    await asyncio.sleep(0.5)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("1. ブランディングページを開きます...")
        await page.goto("https://console.cloud.google.com/auth/branding", wait_until="domcontentloaded", timeout=60000)
        print("   ページロード完了、フォームの表示を待機...")

        # フォーム要素が描画されるまで待機
        if not await wait_for_input(page, "_0rif_mat-input-0", timeout=30):
            print("   フォームが表示されません。ページを再確認...")
            await screenshot(page, "no_form")
            await browser.close()
            return

        await asyncio.sleep(2)

        # Cookie同意バナーを閉じる
        try:
            ok_btn = page.locator("button:has-text('OK')").first
            if await ok_btn.is_visible(timeout=2000):
                await ok_btn.click()
                await asyncio.sleep(1)
        except:
            pass

        # アプリ名を変更
        print(f"2. アプリ名 → '{APP_NAME}'")
        await fill_input(page, "_0rif_mat-input-0", APP_NAME)

        # ホームページURLを入力
        print(f"3. ホームページURL → {HOMEPAGE_URL}")
        await fill_input(page, "_0rif_mat-input-1", HOMEPAGE_URL)

        # プライバシーポリシーURLを入力
        print(f"4. プライバシーポリシーURL → {PRIVACY_URL}")
        await fill_input(page, "_0rif_mat-input-2", PRIVACY_URL)

        await asyncio.sleep(1)

        # 入力値を確認
        values = await page.evaluate("""() => {
            return {
                appName: document.getElementById('_0rif_mat-input-0')?.value,
                homepage: document.getElementById('_0rif_mat-input-1')?.value,
                privacy: document.getElementById('_0rif_mat-input-2')?.value,
                domain: document.getElementById('_0rif_mat-input-4')?.value,
            }
        }""")
        print(f"   確認 - アプリ名: {values['appName']}")
        print(f"   確認 - ホームページ: {values['homepage']}")
        print(f"   確認 - プライバシーポリシー: {values['privacy']}")
        print(f"   確認 - ドメイン: {values['domain']}")

        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await screenshot(page, "filled_top")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await screenshot(page, "filled_bottom")

        # 保存ボタンを押す
        print("5. 保存ボタンを押します...")
        save_btn = page.locator("button:has-text('保存')").first
        if await save_btn.is_visible(timeout=5000):
            await save_btn.click()
            print("   保存クリック完了！")
            await asyncio.sleep(5)
            await screenshot(page, "after_save")
        else:
            print("   保存ボタンが見つかりません")
            await screenshot(page, "no_save")

        # Step 2: 「対象」ページに移動して公開設定を変更
        print("\n6. 「対象」ページに移動して本番公開...")
        await page.click("text=対象")
        await asyncio.sleep(5)
        await screenshot(page, "audience")
        print(f"   URL: {page.url}")

        await browser.close()

asyncio.run(main())
