"""
Comprehensive Automated Verification for SMC Inducement & CHoCH Supply Sniper Indicator
(CHoCH + EQL + Supply Tap) across gold_dashboard.html, index.html, deep_analysis_gold.html
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
        "Dropdown menu toggle": 'id="ind-toggle-smcInducementSupply"',
        "Modal indicator toggle": 'id="modal-toggle-smcInducementSupply"',
        "Indicator title in menu": 'SMC Inducement &amp; CHoCH Supply Sniper',
        "Default config key": 'smcInducementSupply:',
        "Module weight 25%": 'smcInducementSupply: 25,',
        "localStorage key indicator_smc_inducement_active": "localStorage.setItem('indicator_smc_inducement_active'",
        "evaluateSMC_InducementSupply function": 'function evaluateSMC_InducementSupply(',
        "drawSMC_InducementSupplyOverlay function": 'function drawSMC_InducementSupplyOverlay(',
        "CHOCH_SUPPLY in modular tabs": "'CHOCH_SUPPLY'",
        "Short position tool trigger in redrawDrawings": 'window.latestSMC_InducementSupply.isTriggered',
        "EQL liquidity target": 'EQL'
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
    print("\n--- 2. Running Live Edge CDP Test for Inducement & CHoCH Supply Sniper ---")
    user_data = os.path.abspath('edge_inducement_user_data')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    target_url = "file:///D:/trading code try/gold_dashboard.html#terminal"

    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9266",
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
                tabs = requests.get('http://127.0.0.1:9266/json').json()
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

            # Test 1: Check Controls & State Initialization
            t1 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const dropdownChk = document.getElementById('ind-toggle-smcInducementSupply');
                    const modalChk = document.getElementById('modal-toggle-smcInducementSupply');
                    const isConfigActive = window.indicatorSettings ? !!window.indicatorSettings.smcInducementSupply : false;
                    const hasEvalFunc = typeof window.evaluateSMC_InducementSupply === 'function';
                    const hasDrawFunc = typeof window.drawSMC_InducementSupplyOverlay === 'function';
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
            res1 = t1.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 1] Indicator Controls & UI State:")
            print(json.dumps(res1, indent=2))
            assert res1.get("hasDropdownCheckbox"), "Dropdown checkbox missing!"
            assert res1.get("hasModalCheckbox"), "Modal checkbox missing!"
            assert res1.get("hasEvalFunc"), "evaluateSMC_InducementSupply missing!"
            assert res1.get("hasDrawFunc"), "drawSMC_InducementSupplyOverlay missing!"

            # Test 2: Algorithmic State Machine
            # A) Monitoring Phase: Waiting for Inducement Sweep
            t2a = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const candles = [];
                    for (let i = 0; i < 30; i++) {
                        candles.push({ time: 1700000000 + i*300, open: 2700, high: 2702, low: 2698, close: 2701 });
                    }
                    // Supply High at index 10: 2740 (supplyLow = 2736)
                    candles[10] = { time: 1700000000 + 10*300, open: 2736, high: 2740, low: 2735, close: 2738 };
                    // CHoCH Low after drop at index 18: 2700
                    candles[18] = { time: 1700000000 + 18*300, open: 2706, high: 2708, low: 2700, close: 2701 };
                    // Inducement high at index 24: 2722 (X)
                    candles[24] = { time: 1700000000 + 24*300, open: 2715, high: 2722, low: 2714, close: 2720 };
                    // Price hasn't swept inducement yet:
                    candles.push({ time: 1700000000 + 30*300, open: 2718, high: 2720, low: 2716, close: 2719 });

                    return window.evaluateSMC_InducementSupply(candles);
                })()
                """,
                "returnByValue": True
            }, msg_id=20)
            res2a = t2a.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 2A] Phase 3 (Monitoring / Waiting for Inducement Sweep):")
            print(json.dumps(res2a, indent=2))
            assert res2a.get("isTriggered") is False, "Should be waiting for sweep!"
            assert res2a.get("stateBadge") == "WAITING FOR INDUCEMENT SWEEP"
            assert res2a.get("direction") == "STANDBY"
            assert "Waiting for Inducement sweep" in res2a.get("reason", "")

            # B) Phase 4 & 5: Inducement Purge & Extreme Supply Tap with Rejection
            t2b = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    const candles = [];
                    for (let i = 0; i < 30; i++) {
                        candles.push({ time: 1700000000 + i*300, open: 2700, high: 2702, low: 2698, close: 2701 });
                    }
                    // Supply High at index 10: 2740 (supplyLow = 2736)
                    candles[10] = { time: 1700000000 + 10*300, open: 2736, high: 2740, low: 2735, close: 2738 };
                    // CHoCH Low after drop at index 18: 2700
                    candles[18] = { time: 1700000000 + 18*300, open: 2706, high: 2708, low: 2700, close: 2701 };
                    // Equal Low at index 20: 2700.30
                    candles[20] = { time: 1700000000 + 20*300, open: 2705, high: 2707, low: 2700.30, close: 2703 };
                    // Inducement high at index 24: 2722 (X)
                    candles[24] = { time: 1700000000 + 24*300, open: 2715, high: 2722, low: 2714, close: 2720 };
                    // Trigger Bar: sweeps 2722, taps 2736+ supply, prints strong upper rejection wick (33%) and bearish close
                    candles.push({ time: 1700000000 + 30*300, open: 2737, high: 2739.5, low: 2732, close: 2734 });

                    const setup = window.evaluateSMC_InducementSupply(candles);
                    window.latestSMC_InducementSupply = setup;

                    // Update telemetry UI & switch tab to CHOCH_SUPPLY
                    window.switchModularTab('CHOCH_SUPPLY');
                    window.updateModularEngineTelemetry(candles, 2734);
                    if (typeof window.redrawDrawings === 'function') window.redrawDrawings();

                    const telemetryData = window.modularEngineState.indicators.CHOCH_SUPPLY;
                    const activeTab = window.modularEngineState.activeTab;
                    const cardHtml = document.getElementById('modular-indicator-telemetry').innerHTML;

                    return {
                        setup,
                        telemetryData,
                        activeTab,
                        hasCardTitle: cardHtml.includes('⚡ SMC INDUCEMENT') && cardHtml.includes('CHOCH SUPPLY SNIPER'),
                        hasRetestBadge: cardHtml.includes('SUPPLY MITIGATION CONFIRMED'),
                        hasEQLTarget: cardHtml.includes(setup.tp)
                    };
                })()
                """,
                "returnByValue": True
            }, msg_id=30)
            res2b = t2b.get("result", {}).get("result", {}).get("value", {})
            print("\n[TEST 2B] Phase 5 (Trigger Execution) & Modular Telemetry Card:")
            print(json.dumps(res2b, indent=2))
            assert res2b.get("setup", {}).get("isTriggered") is True, "Inducement & Supply Tap trigger failed!"
            assert res2b.get("setup", {}).get("direction") == "SELL"
            assert res2b.get("hasCardTitle") is True, "Telemetry card title not rendered!"
            assert res2b.get("hasRetestBadge") is True, "SUPPLY MITIGATION CONFIRMED badge missing!"

            # Test 3: LocalStorage Persistence & Dynamic Sync
            t3 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": """
                (() => {
                    // Turn OFF
                    window.toggleModularIndicator('smcInducementSupply', false);
                    const savedOff = localStorage.getItem('indicator_smc_inducement_active');
                    const dropOff = document.getElementById('ind-toggle-smcInducementSupply').checked;

                    // Turn ON
                    window.toggleModularIndicator('smcInducementSupply', true);
                    const savedOn = localStorage.getItem('indicator_smc_inducement_active');
                    const dropOn = document.getElementById('ind-toggle-smcInducementSupply').checked;

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
            screenshot_path = r"C:\Users\SP\.gemini\antigravity\brain\202ca59f-5839-4e7b-b818-02eec490772b\smc_inducement_sniper_verified.png"
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(shot["result"]["data"]))
            print(f"\n[PASS] Screenshot saved to: {screenshot_path}")

            print("\n>>> ALL SMC INDUCEMENT & CHOCH SUPPLY SNIPER TESTS PASSED 100%! <<<")
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
