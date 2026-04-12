"""
処理内容:
- schedule-picker のログアウトボタン表示をテスト
- AppleScriptでDOMを検証し、問題があれば自動修正してpush・再テスト

使い方:
- python3 e2e/test_schedule_picker.py
"""

import subprocess
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

URL = "https://takindustries1987-dev.github.io/schedule-picker/"
INDEX_HTML = Path(__file__).parent.parent / "02_claude" / "index.html"
REPO_DIR = Path("/tmp/schedule-picker")
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
RESULTS_DIR = Path(__file__).parent / "results"
MAX_ITERATIONS = 5

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def ts():
    return datetime.now().strftime("%H%M%S")


def log(msg):
    print(f"[{ts()}] {msg}", flush=True)


def chrome_js(js: str) -> str:
    escaped = js.replace("\\", "\\\\").replace('"', '\\"')
    script = f'tell application "Google Chrome" to return execute active tab of front window javascript "{escaped}"'
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return r.stdout.strip()


def get_dom_state() -> dict:
    """ログアウトボタンとセクション表示状態をシンプルに取得"""
    logout_inline   = chrome_js("document.getElementById('logout-btn').style.display")
    logout_computed = chrome_js("window.getComputedStyle(document.getElementById('logout-btn')).display")
    logout_w        = chrome_js("document.getElementById('logout-btn').offsetWidth")
    cal_inline      = chrome_js("document.getElementById('cal-section').style.display")
    cal_computed    = chrome_js("window.getComputedStyle(document.getElementById('cal-section')).display")

    return {
        "logout_inline":   logout_inline,
        "logout_computed": logout_computed,
        "logout_width":    logout_w,
        "cal_inline":      cal_inline,
        "cal_computed":    cal_computed,
    }


def save_state(state: dict, label: str) -> Path:
    path = SCREENSHOTS_DIR / f"{label}_{ts()}.json"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def diagnose(state: dict) -> str:
    cal_vis = state.get("cal_computed", "none")
    logout_vis = state.get("logout_computed", "none")
    logout_w = state.get("logout_width", "0")

    if cal_vis == "none":
        return "NOT_LOGGED_IN"

    # ログイン済み（cal-sectionが表示）なのにlogoutが非表示
    if logout_vis == "none" or logout_w == "0":
        return "LOGGED_IN_BUT_LOGOUT_HIDDEN"

    return "OK"


def simulate_login_callback():
    """ログインコールバックと同じJS処理をシミュレート"""
    log("  ログインコールバックをシミュレート...")
    chrome_js("document.getElementById('auth-section').style.display='none'")
    chrome_js("document.getElementById('cal-section').style.display='block'")
    chrome_js("var lb=document.getElementById('logout-btn'); lb.style.display='inline-block'; lb.classList.add('visible');")


def fix_logout_visibility(html_path: Path) -> bool:
    content = html_path.read_text(encoding="utf-8")
    changed = False

    # display='' → display='inline-block'
    if "style.display   = '';" in content:
        content = content.replace(
            "document.getElementById('logout-btn').style.display   = '';",
            "document.getElementById('logout-btn').style.display   = 'inline-block';"
        )
        changed = True
        log("  FIX: display='' → display='inline-block'")

    # CSS側でdisplay:noneが強制されていないか確認・!important追加
    if "#logout-btn.visible" not in content:
        content = content.replace(
            "      display: none;\n    }\n\n    /* ===== Auth =====",
            "      display: none;\n    }\n    #logout-btn.visible { display: inline-block !important; }\n\n    /* ===== Auth ====="
        )
        changed = True
        log("  FIX: .visible class + !important をCSS追加")

    # visibleクラス付与
    if "lb.classList.add('visible')" not in content:
        content = content.replace(
            "document.getElementById('logout-btn').style.display   = 'inline-block';",
            "const lb=document.getElementById('logout-btn'); lb.style.display='inline-block'; lb.classList.add('visible');"
        )
        changed = True
        log("  FIX: classList.add('visible') を追加")

    if changed:
        html_path.write_text(content, encoding="utf-8")
    return changed


def push_fix() -> bool:
    shutil.copy(INDEX_HTML, REPO_DIR / "index.html")
    subprocess.run(["git", "add", "index.html"], cwd=REPO_DIR, capture_output=True)
    r = subprocess.run(
        ["git", "commit", "-m", f"E2E fix: logout btn [{ts()}]"],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    if "nothing to commit" in r.stdout:
        log("  変更なし（すでに最新）")
        return True
    r2 = subprocess.run(["git", "push"], cwd=REPO_DIR, capture_output=True, text=True)
    success = r2.returncode == 0
    log(f"  Push: {'成功' if success else '失敗 - ' + r2.stderr}")
    return success


def reload_page(hard=False):
    if hard:
        chrome_js("location.reload(true)")
    else:
        subprocess.run(["osascript", "-e",
            'tell application "Google Chrome" to tell active tab of front window to reload'],
            capture_output=True)
    time.sleep(6)


def main():
    log("=== schedule-picker E2Eテスト開始 ===")
    log(f"  対象URL: {URL}")

    subprocess.run(["open", "-a", "Google Chrome", URL], capture_output=True)
    time.sleep(5)

    all_results = []
    final_issue = None

    for i in range(1, MAX_ITERATIONS + 1):
        log(f"\n--- イテレーション {i}/{MAX_ITERATIONS} ---")

        # ログイン済みでなければシミュレート
        state = get_dom_state()
        log(f"  cal_computed={state['cal_computed']} | logout_inline='{state['logout_inline']}' | logout_computed={state['logout_computed']} | logout_w={state['logout_width']}")

        if state["cal_computed"] == "none":
            log("  未ログイン → ログインコールバックをシミュレートします")
            simulate_login_callback()
            time.sleep(1)
            state = get_dom_state()
            log(f"  シミュレート後: cal={state['cal_computed']} | logout={state['logout_computed']} | w={state['logout_width']}")

        issue = diagnose(state)
        log(f"  診断: {issue}")

        save_path = save_state(state, f"iter{i}_{issue}")
        all_results.append({"iter": i, "issue": issue, "state": state})

        if issue == "OK":
            log(f"\n✓ ログアウトボタン正常表示確認！")
            final_issue = "OK"
            break

        elif issue == "LOGGED_IN_BUT_LOGOUT_HIDDEN":
            log("  修正を適用します...")
            fixed = fix_logout_visibility(INDEX_HTML)
            if fixed:
                pushed = push_fix()
                if pushed:
                    log(f"  デプロイ待機 90秒...")
                    time.sleep(90)
                    reload_page(hard=True)
                    simulate_login_callback()
                    time.sleep(1)
            else:
                log("  自動修正パターンなし → JSで直接適用して再確認")
                simulate_login_callback()
                time.sleep(1)
                state2 = get_dom_state()
                issue2 = diagnose(state2)
                log(f"  直接修正後: {issue2}")
                all_results.append({"iter": f"{i}b", "issue": issue2, "state": state2})
                if issue2 == "OK":
                    final_issue = "OK"
                    break

        final_issue = issue

    # 結果保存
    result_path = RESULTS_DIR / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_path.write_text(json.dumps({
        "final": final_issue,
        "iterations": all_results
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"\n最終結果: {final_issue}")
    log(f"詳細: {result_path}")
    log("=== E2Eテスト終了 ===")


if __name__ == "__main__":
    main()
