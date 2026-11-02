"""
Comprehensive Automated Verification for SMC M5 Pullback Sniper Indicator
(BOS + OB 0.618 + IFVG TP) across gold_dashboard.html, index.html, deep_analysis_gold.html
"""

import subprocess
import asyncio
import json
import base64
import os
import sys
import requests
import websockets

sys.stdout.reconfigure(encoding='utf-8')

def check_html_files():
    print("\n--- 1. Static HTML & Code Verification across Files ---")
    files = ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']
    all_ok = True

    checks = {
        "Dropdown menu toggle": 'id="ind-toggle-smcPullbackSniper"',
        "Modal indicator toggle": 'id="modal-toggle-smcPullbackSniper"',
        "Indicator title in menu": 'SMC Pullback Sniper (BOS + OB 0.618 + IFVG TP)',
        "Default config key": 'smcPullbackSniper:',
        "Module weight 25%": 'smcPullbackSniper: 25,',
        "localStorage key indicator_ob_fibo_active": "localStorage.setItem('indicator_ob_fibo_active'",
        "evaluateSMC_OB_FiboSetup function": 'function evaluateSMC_OB_FiboSetup(',
        "drawSMC_OB_FiboOverlay function": 'function drawSMC_OB_FiboOverlay(',
        "OB_FIBO in modular tabs": "'OB_FIBO'",
        "Short position tool trigger in redrawDrawings": 'window.latestSMC_OB_Fibo.isTriggered',
        "1:3.8 RR target text": '1:3.8 RR'
    }

    for fname in files:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"\nChecking {fname}:")
        file_ok = True
        for name, query in checks.items():
            if query in content:
                print(f"  [PASS] {name}")
            else:
                print(f"  [FAIL] {name}")
                file_ok = False
        if not file_ok:
            all_ok = False

    return all_ok

async def send_cmd(ws, method, params=None, msg_id=1):
    req = {"id": msg_id, "method": method}
    if params:
        req["params"] = params
    await ws.send(json.dumps(req))
    while True:
        raw = await ws.recv()
        msg = json.loads(raw)
        if msg.get("id") == msg_id:
            return msg

async def run_cdp_verification():
    print("\n--- 2. Running Live Edge CDP Test for State Machine, Canvas & Telemetry ---")
    user_data = os.path.abspath('edge_sniper_user_data')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    target_url = "file:///D:/trading code try/gold_dashboard.html#terminal"

    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9256",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--window-size=1280,900",
        target_url
    ])

    try:
        ws_url = None
        for attempt in range(25):
            try:
                tabs = requests.get('http://127.0.0.1:9256/json').json()
                for t in tabs:
                    if 'gold_dashboard' in t.get('url', ''):
                        ws_url = t['webSocketDebuggerUrl']
                        break
                if ws_url:
                    break
            except Exception:
                pass
            await asyncio.sleep(0.5)

        if not ws_url:
            print("[ERROR] Failed to connect to Edge tab!")
            return False

        async with websockets.connect(ws_url, max_size=30*1024*1024) as ws:
            print("[x] Connected to Edge CDP on desktop viewport (1280x900)!")
            await send_cmd(ws, "Runtime.enable", msg_id=1)
            await send_cmd(ws, "Page.enable", msg_id=2)
            await asyncio.sleep(3.0)

            # Test 1: Check Toggle & Settings initialization
            t1 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const dropdownChk = document.getElementById('ind-toggle-smcPullbackSniper');
                    const modalChk = document.getElementById('modal-toggle-smcPullbackSniper');
                    const isConfigActive = window.indicatorSettings ? !!window.indicatorSettings.smcPullbackSniper : false;
                    const hasEvalFunc = typeof window.evaluateSMC_OB_FiboSetup === 'function';
                    const hasDrawFunc = typeof window.drawSMC_OB_FiboOverlay === 'function';
                    const countBadge = document.getElementById('activeIndCountBadge') ? document.getElementById('activeIndCountBadge').innerText : '';
                    const weightBadge = document.getElementById('totalActiveWeightBadge') ? document.getElementById('totalActiveWeightBadge').innerText : '';

                    return {
                        hasDropdownCheckbox: !!dropdownChk,
                        dropdownChecked: dropdownChk ? dropdownChk.checked : false,
                        hasModalCheckbox: !!modalChk,
                        modalChecked: modalChk ? modalChk.checked : false,
                        isConfigActive,
                        hasEvalFunc,
                        hasDrawFunc,
                        countBadge,
                        weightBadge
                    };
                })()
                """,
                "returnByValue": True
            }, msg_id=10)
            print("\n[TEST 1] Raw t1 response:")
            print(json.dumps(t1, indent=2))
            res1 = t1.get("result", {}).get("result", {}).get("value", {})
            assert res1.get("hasDropdownCheckbox"), "Dropdown checkbox missing!"
            assert res1.get("hasModalCheckbox"), "Modal checkbox missing!"
            assert res1.get("hasEvalFunc"), "evaluateSMC_OB_FiboSetup missing!"
            assert res1.get("hasDrawFunc"), "drawSMC_OB_FiboOverlay missing!"

            # Test 2: Algorithmic State Machine (States 1, 2, 3, 4, 5)
            # A) State 3: Pullback Monitor (Waiting Pullback)
            t2a = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const candles = [];
                    for (let i = 0; i < 30; i++) {
                        candles.push({ time: 1700000000 + i*300, open: 2700, high: 2702, low: 2698, close: 2701 });
                    }
                    // Swing High (OB green candle):
                    candles[15] = { time: 1700000000 + 15*300, open: 2720, high: 2730, low: 2718, close: 2728 };
                    // Impulse drop (BOS):
                    candles[16] = { time: 1700000000 + 16*300, open: 2728, high: 2729, low: 2710, close: 2712 };
                    candles[17] = { time: 1700000000 + 17*300, open: 2712, high: 2714, low: 2705, close: 2706 };
                    candles[18] = { time: 1700000000 + 18*300, open: 2706, high: 2708, low: 2700, close: 2701 }; // Swing Low: 2700
                    // Price consolidating at low, not yet pulled back:
                    candles.push({ time: 1700000000 + 30*300, open: 2702, high: 2704, low: 2701, close: 2703 });

                    return window.evaluateSMC_OB_FiboSetup(candles);
                })()
                """,
                "returnByValue": True
            }, msg_id=20)
            res2a = t2a.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 2A] State 3 (Pullback Monitor):")
            print(json.dumps(res2a, indent=2))
            assert res2a.get("isTriggered") is False, "Should be waiting pullback!"
            assert res2a.get("stateBadge") == "WAITING PULLBACK"
            assert res2a.get("direction") == "STANDBY"
            assert "Waiting for retracement pullback" in res2a.get("reason", "")

            # B) State 4: Trigger Confluence (OB + FIBO 0.618 Retest + Rejection Wick)
            t2b = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const candles = [];
                    for (let i = 0; i < 30; i++) {
                        candles.push({ time: 1700000000 + i*300, open: 2700, high: 2702, low: 2698, close: 2701 });
                    }
                    candles[15] = { time: 1700000000 + 15*300, open: 2720, high: 2730, low: 2718, close: 2728 };
                    candles[16] = { time: 1700000000 + 16*300, open: 2728, high: 2729, low: 2710, close: 2712 };
                    candles[17] = { time: 1700000000 + 17*300, open: 2712, high: 2714, low: 2705, close: 2706 };
                    candles[18] = { time: 1700000000 + 18*300, open: 2706, high: 2708, low: 2700, close: 2701 };
                    
                    // fibo 0.618 = 2700 + (30 * 0.618) = 2718.54. obLevel = 2730. confluence = 2724.27
                    const confluence = (2718.54 + 2730) / 2;
                    // Current bar taps confluence with strong upper rejection wick
                    candles.push({ time: 1700000000 + 30*300, open: 2722, high: confluence + 0.5, low: 2720, close: 2721 });

                    const setup = window.evaluateSMC_OB_FiboSetup(candles);
                    window.latestSMC_OB_Fibo = setup;

                    // Update telemetry UI & switch tab to OB_FIBO
                    window.switchModularTab('OB_FIBO');
                    window.updateModularEngineTelemetry(candles, 2721);
                    if (typeof window.redrawDrawings === 'function') window.redrawDrawings();

                    const telemetryData = window.modularEngineState.indicators.OB_FIBO;
                    const activeTab = window.modularEngineState.activeTab;
                    const cardHtml = document.getElementById('modular-indicator-telemetry').innerHTML;

                    return {
                        setup,
                        telemetryData,
                        activeTab,
                        hasCardTitle: cardHtml.includes('⚡ SMC PULLBACK SNIPER (OB + 0.618 FIB)'),
                        hasRetestBadge: cardHtml.includes('0.618 RETEST CONFIRMED'),
                        hasRRText: cardHtml.includes('1 : 3.8')
                    };
                })()
                """,
                "returnByValue": True
            }, msg_id=30)
            res2b = t2b.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 2B] State 4 (Trigger Confluence) & Modular Telemetry Card:")
            print(json.dumps(res2b, indent=2))
            assert res2b.get("setup", {}).get("isTriggered") is True, "State 4 Confluence trigger failed!"
            assert res2b.get("setup", {}).get("direction") == "SELL"
            assert res2b.get("setup", {}).get("rr") == "1 : 3.8"
            assert res2b.get("hasCardTitle") is True, "Telemetry card title not rendered!"
            assert res2b.get("hasRetestBadge") is True, "0.618 RETEST CONFIRMED badge missing!"
            assert res2b.get("hasRRText") is True, "1 : 3.8 RR missing in telemetry card!"

            # Test 3: LocalStorage Latching and Toggle Synchronization
            t3 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    // Turn OFF
                    window.toggleModularIndicator('smcPullbackSniper', false);
                    const savedOff = localStorage.getItem('indicator_ob_fibo_active');
                    const dropOff = document.getElementById('ind-toggle-smcPullbackSniper').checked;

                    // Turn ON
                    window.toggleModularIndicator('smcPullbackSniper', true);
                    const savedOn = localStorage.getItem('indicator_ob_fibo_active');
                    const dropOn = document.getElementById('ind-toggle-smcPullbackSniper').checked;

                    return { savedOff, dropOff, savedOn, dropOn };
                })()
                """,
                "returnByValue": True
            }, msg_id=40)
            res3 = t3.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 3] LocalStorage Persistence & Dynamic Sync:")
            print(json.dumps(res3, indent=2))
            assert res3.get("savedOff") == "false" and res3.get("dropOff") is False
            assert res3.get("savedOn") == "true" and res3.get("dropOn") is True

            # Capture high-resolution screenshot
            await asyncio.sleep(1.0)
            shot = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=50)
            screenshot_path = r"C:\Users\SP\.gemini\antigravity\brain\202ca59f-5839-4e7b-b818-02eec490772b\smc_pullback_sniper_verified.png"
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(shot["result"]["data"]))
            print(f"\n[PASS] Screenshot saved to: {screenshot_path}")

            print("\n>>> ALL SMC PULLBACK SNIPER INDICATOR TESTS PASSED 100%! <<<")
            return True

    finally:
        proc.terminate()

def main():
    if not check_html_files():
        print("[FAIL] Static checks failed!")
        sys.exit(1)

    ok = asyncio.run(run_cdp_verification())
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
