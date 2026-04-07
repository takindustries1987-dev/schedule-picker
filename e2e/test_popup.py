"""
処理内容: イベント付きスロットのポップアップ表示を再帰的にテスト
使い方: python3 e2e/test_popup.py (Chrome がリモートデバッグポート9222で起動済み)
"""
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime

CDP_URL = "http://localhost:9222"
URL = "https://takindustries1987-dev.github.io/schedule-picker/"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
MAX_RETRIES = 5


def ts():
    return datetime.now().strftime("%H%M%S")


async def screenshot(page, name):
    path = SCREENSHOTS_DIR / f"{name}_{ts()}.png"
    await page.screenshot(path=str(path), full_page=True)
    print(f"   screenshot: {path}")
    return path


async def check_popup(page, iteration):
    print(f"\n--- イテレーション {iteration}/{MAX_RETRIES} ---")

    # Step 1: ページの状態を確認
    state = await page.evaluate("""() => {
        const calSection = document.getElementById('cal-section');
        const calVisible = calSection && window.getComputedStyle(calSection).display !== 'none';
        const blockedSlots = document.querySelectorAll('.slot.blocked');
        const evFreeSlots = document.querySelectorAll('.slot.ev-free');
        const evMapKeys = Object.keys(window.evMap || {}).length;

        // blockedスロットのeventListener確認
        const firstBlocked = blockedSlots[0];
        let clickListenerInfo = 'no blocked slots';
        if (firstBlocked) {
            clickListenerInfo = `onclick=${!!firstBlocked.onclick}, classes=${firstBlocked.className}`;
        }

        // evMapのサンプルエントリ
        let evMapSample = null;
        const keys = Object.keys(window.evMap || {});
        if (keys.length > 0) {
            evMapSample = { key: keys[0], value: window.evMap[keys[0]] };
        }

        return {
            calVisible,
            blockedCount: blockedSlots.length,
            evFreeCount: evFreeSlots.length,
            evMapKeys,
            clickListenerInfo,
            evMapSample,
            showEvPopupExists: typeof window.showEvPopup === 'function',
        };
    }""")

    print(f"   calVisible: {state['calVisible']}")
    print(f"   blockedSlots: {state['blockedCount']}")
    print(f"   evFreeSlots: {state['evFreeCount']}")
    print(f"   evMapKeys: {state['evMapKeys']}")
    print(f"   clickListenerInfo: {state['clickListenerInfo']}")
    print(f"   showEvPopupExists: {state['showEvPopupExists']}")
    print(f"   evMapSample: {state['evMapSample']}")

    await screenshot(page, f"iter{iteration}_state")

    if not state['calVisible']:
        print("   ERROR: カレンダーが非表示（未ログイン）")
        return 'NOT_LOGGED_IN'

    if state['evMapKeys'] == 0:
        print("   ERROR: evMapが空（予定なし）")
        return 'NO_EVENTS'

    total_event_slots = state['blockedCount'] + state['evFreeCount']
    if total_event_slots == 0:
        print("   ERROR: イベント付きスロットが0件")
        return 'NO_EVENT_SLOTS'

    # Step 2: showEvPopupを直接呼び出してポップアップが表示されるか確認
    print("   showEvPopupを直接呼び出しテスト...")
    popup_result = await page.evaluate("""() => {
        const keys = Object.keys(window.evMap || {});
        if (keys.length === 0) return { success: false, reason: 'no evMap entries' };

        // 最初のイベントキーで呼び出し
        const key = keys[0];
        try {
            showEvPopup(key);
        } catch(e) {
            return { success: false, reason: e.message };
        }

        // ポップアップが表示されたか確認
        const overlay = document.querySelector('.ev-popup-overlay');
        if (overlay) {
            const popup = overlay.querySelector('.ev-popup');
            const title = popup ? popup.querySelector('.ev-popup-title')?.textContent : '';
            const time = popup ? popup.querySelector('.ev-popup-time')?.textContent : '';
            // 閉じる
            overlay.remove();
            return { success: true, title, time, key };
        }
        return { success: false, reason: 'popup overlay not found after calling showEvPopup' };
    }""")

    print(f"   直接呼び出し結果: {popup_result}")
    await screenshot(page, f"iter{iteration}_directcall")

    if not popup_result.get('success'):
        print(f"   ERROR: showEvPopup直接呼び出し失敗: {popup_result.get('reason')}")
        return 'POPUP_FUNCTION_BROKEN'

    # Step 3: 実際のクリックでポップアップが表示されるか確認
    print("   実際のクリックテスト...")

    # イベント付きスロットを探してクリック
    click_result = await page.evaluate("""() => {
        const slots = document.querySelectorAll('.slot.blocked, .slot.ev-free');
        if (slots.length === 0) return { clicked: false, reason: 'no event slots' };

        // 先頭のイベントスロットを取得
        const slot = slots[0];
        const rect = slot.getBoundingClientRect();
        return {
            clicked: true,
            rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
            classes: slot.className,
            hasOnclick: !!slot.onclick,
        };
    }""")

    print(f"   クリック対象: {click_result}")

    if click_result.get('clicked') and click_result.get('rect'):
        rect = click_result['rect']
        x = rect['x'] + rect['w'] / 2
        y = rect['y'] + rect['h'] / 2

        # Playwrightで実際にクリック
        await page.mouse.click(x, y)
        await asyncio.sleep(1)

        # ポップアップが表示されたか
        has_popup = await page.evaluate("() => !!document.querySelector('.ev-popup-overlay')")
        await screenshot(page, f"iter{iteration}_afterclick")

        if has_popup:
            print("   SUCCESS: ポップアップ表示確認！")
            # 閉じる
            await page.evaluate("() => document.querySelector('.ev-popup-overlay')?.remove()")
            return 'OK'
        else:
            print("   ERROR: クリックしたがポップアップ非表示")

            # getEventListenersの代わりにクリックイベントを手動発火
            print("   手動dispatchEvent('click')テスト...")
            dispatch_result = await page.evaluate("""() => {
                const slots = document.querySelectorAll('.slot.blocked, .slot.ev-free');
                if (slots.length === 0) return 'no slots';
                const slot = slots[0];
                slot.dispatchEvent(new MouseEvent('click', { bubbles: true }));

                // 少し待ってから確認
                return new Promise(resolve => {
                    setTimeout(() => {
                        const overlay = document.querySelector('.ev-popup-overlay');
                        if (overlay) {
                            overlay.remove();
                            resolve('popup_shown');
                        } else {
                            resolve('no_popup');
                        }
                    }, 500);
                });
            }""")
            print(f"   dispatchEvent結果: {dispatch_result}")

            # consoleログを確認
            return 'CLICK_NOT_WORKING'

    return 'UNKNOWN'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]

        # 既存のタブからschedule-pickerが開いているものを探す
        target_page = None
        for pg in context.pages:
            if 'schedule-picker' in pg.url or 'github.io' in pg.url:
                target_page = pg
                break

        if not target_page:
            print("schedule-pickerのタブが見つかりません。新しいタブで開きます。")
            target_page = await context.new_page()
            await target_page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)

        print(f"=== ポップアップE2Eテスト開始 ===")
        print(f"URL: {target_page.url}")

        # consoleログを収集
        logs = []
        target_page.on('console', lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        final_result = None
        for i in range(1, MAX_RETRIES + 1):
            result = await check_popup(target_page, i)
            final_result = result

            if result == 'OK':
                break
            elif result == 'NOT_LOGGED_IN':
                print("   → ログインが必要です。ブラウザでログインしてから再実行してください。")
                break
            elif result in ('POPUP_FUNCTION_BROKEN', 'CLICK_NOT_WORKING'):
                print(f"   → 問題を検出: {result}")
                if logs:
                    print(f"   consoleログ:")
                    for log in logs[-10:]:
                        print(f"     {log}")
                break

        print(f"\n=== 最終結果: {final_result} ===")
        if logs:
            print(f"consoleログ ({len(logs)}件):")
            for log in logs[-20:]:
                print(f"  {log}")

        await browser.close()

asyncio.run(main())
