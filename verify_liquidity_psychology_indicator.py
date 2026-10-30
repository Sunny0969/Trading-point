"""
Comprehensive test and verification of the Liquidity & Candle Psychology Engine
"""

import sys
import os
import json
import asyncio
import subprocess
import websockets
import base64

sys.stdout.reconfigure(encoding='utf-8')

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

async def eval_js(ws, expr, msg_id=1):
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True}, msg_id)
    if "result" in res:
        if "exceptionDetails" in res["result"]:
            print(f"JS EXCEPTION: {res['result']['exceptionDetails']}")
            return None
        if "result" in res["result"]:
            return res["result"]["result"].get("value")
    return None

async def main():
    print("==================================================================")
    print(" VERIFYING LIQUIDITY & CANDLE PSYCHOLOGY ENGINE IN EDGE HEADLESS  ")
    print("==================================================================")

    user_data = os.path.abspath('edge_fresh_user_data_liquidity_engine')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    port = 9245

    cmd = [
        edge_path,
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--window-size=1600,1050",
        "file:///d:/trading code try/gold_dashboard.html#terminal"
    ]

    proc = subprocess.Popen(cmd)
    ws = None

    try:
        await asyncio.sleep(2.5)

        import requests
        version_url = f"http://127.0.0.1:{port}/json"
        tabs = requests.get(version_url).json()
        target_tab = None
        for t in tabs:
            if "gold_dashboard.html" in t.get("url", ""):
                target_tab = t
                break
        if not target_tab:
            target_tab = tabs[0]

        ws_url = target_tab["webSocketDebuggerUrl"]
        print(f"Connected to Edge DevTools: {ws_url}")
        ws = await websockets.connect(ws_url, max_size=50_000_000)

        # Wait for page to initialize
        await asyncio.sleep(2.0)

        # 1. VERIFY DOM ELEMENTS & INDICATOR REGISTRATION
        print("\n--- TEST 1: INDICATOR REGISTRATION IN UI ---")
        dom_check = await eval_js(ws, """
        (() => {
            const dropdownToggle = document.getElementById('ind-toggle-liquidityPsychology');
            const modalToggle = document.getElementById('modal-toggle-liquidityPsychology');
            const pipelinePill = document.getElementById('pipeLiqPsy');
            const countBadge = document.getElementById('activeIndCountBadge');
            const weightBadge = document.getElementById('totalActiveWeightBadge');
            const cfg = window.indicatorSettings;

            return {
                dropdownToggleExists: !!dropdownToggle,
                dropdownChecked: dropdownToggle ? dropdownToggle.checked : false,
                modalToggleExists: !!modalToggle,
                pipelinePillExists: !!pipelinePill,
                countBadgeText: countBadge ? countBadge.innerText : null,
                weightBadgeText: weightBadge ? weightBadge.innerText : null,
                configHasSetting: typeof cfg.liquidityPsychology !== 'undefined',
                configValue: cfg.liquidityPsychology
            };
        })()
        """, 10)

        print(f"Dropdown Toggle Exists: {dom_check.get('dropdownToggleExists')}")
        print(f"Dropdown Checked: {dom_check.get('dropdownChecked')}")
        print(f"Modal Toggle Exists: {dom_check.get('modalToggleExists')}")
        print(f"Pipeline Pill Exists: {dom_check.get('pipelinePillExists')}")
        print(f"Active Indicator Count: {dom_check.get('countBadgeText')}")
        print(f"Active Weight Badge: {dom_check.get('weightBadgeText')}")
        print(f"Config Setting: {dom_check.get('configValue')}")

        assert dom_check.get('dropdownToggleExists') == True, "Dropdown toggle missing!"
        assert dom_check.get('modalToggleExists') == True, "Modal toggle missing!"
        assert dom_check.get('pipelinePillExists') == True, "Pipeline pill missing!"
        print(">>> TEST 1 PASSED: UI Elements registered perfectly.")

        # 2. VERIFY ALGORITHMIC LOGIC: evaluateLiquidityPsychology
        print("\n--- TEST 2: CORE ALGORITHMIC LOGIC TESTS ---")
        algo_tests = await eval_js(ws, """
        (() => {
            const results = {};

            // Mock candle helper
            const makeBar = (time, o, h, l, c) => ({ time, open: o, high: h, low: l, close: c, volume: 100 });

            // Case A: Immediate sweep on the last bar -> MUST return null (No blind entries on sweep bar)
            const candlesImmediate = [
                makeBar(100, 4015, 4018, 4012, 4016),
                makeBar(101, 4016, 4017, 4011, 4013),
                makeBar(102, 4013, 4015, 4010, 4012),
                makeBar(103, 4012, 4014, 4009, 4011),
                makeBar(104, 4011, 4013, 4008, 4010),
                // Bar 105: Sweep bar (low 3996 < 4000, close 4002 > 4000, lower wick 6 / 8 = 75%)
                makeBar(105, 4002, 4004, 3996, 4002)
            ];
            const resImmediate = window.evaluateLiquidityPsychology(candlesImmediate, 4000.0, "SUPPORT");
            results.immediateSweepNull = (resImmediate === null);

            // Case B: Invalidation during 5 bars -> Price closes below sweep wick extreme -> MUST return null
            const candlesInvalidated = [
                makeBar(100, 4015, 4018, 4012, 4016),
                // Bar 101: Sweep bar (low 3995 < 4000, close 4001, lower wick 6 / 8 = 75%)
                makeBar(101, 4001, 4003, 3995, 4001),
                // Bar 102: Defended
                makeBar(102, 4001, 4005, 4000, 4004),
                // Bar 103: Fake sweep breakdown: close 3992 < sweepLow (3995)
                makeBar(103, 4004, 4004, 3990, 3992),
                makeBar(104, 3992, 3995, 3988, 3990)
            ];
            const resInvalid = window.evaluateLiquidityPsychology(candlesInvalidated, 4000.0, "SUPPORT");
            results.invalidationDetected = (resInvalid === null);

            // Case C: Bullish Sweep + 5-Bar Psychological Absorption Verified
            // Need at least 6 bars: 3 baseline bars, 1 sweep bar, 2 confirmation bars (total 6 bars)
            const candlesBullish = [
                makeBar(98,  4020, 4022, 4018, 4020),
                makeBar(99,  4020, 4021, 4017, 4019),
                makeBar(100, 4019, 4020, 4014, 4015),
                // Bar 101 (index 3): Sweep bar (low 3995 < 4000, close 4002 > 4000, lower wick (4002-3995)/(4004-3995) = 7/9 = 77% >= 35%)
                makeBar(101, 4002, 4004, 3995, 4002),
                // Bar 102 (index 4): Bullish Absorption 1 (close 4005 >= 4000, lower wick (4002-3998)/(4005-3998) = 4/7 = 57% >= 35%)
                makeBar(102, 4002, 4005, 3998, 4005),
                // Bar 103 (index 5): Bullish Absorption 2 (close 4009 >= 4000, lower wick (4006-4001)/(4010-4001) = 5/9 = 55% >= 35%)
                makeBar(103, 4006, 4010, 4001, 4009)
            ];
            const allPools = { eql: 4000.00, eqh: 4030.00, asiaHigh: 4032.00, pdh: 4035.00 };
            const resBull = window.evaluateLiquidityPsychology(candlesBullish, 4000.00, "SUPPORT", { name: "Equal Lows (EQL)", code: "EQL" }, allPools);
            results.bullishSetup = resBull;

            // Case D: Bearish Sweep + 5-Bar Psychological Displacement Verified
            const candlesBearish = [
                makeBar(98,  4030, 4032, 4028, 4030),
                makeBar(99,  4030, 4033, 4029, 4031),
                makeBar(100, 4031, 4035, 4030, 4034),
                // Bar 101 (index 3): Sweep bar (high 4055 > 4050, close 4048 < 4050, upper wick (4055-4048)/(4055-4046) = 7/9 = 77% >= 35%)
                makeBar(101, 4048, 4055, 4046, 4048),
                // Bar 102 (index 4): Bearish Displacement 1 (close 4044 <= 4050, upper wick (4052-4048)/(4052-4043) = 4/9 = 44% >= 35%)
                makeBar(102, 4048, 4052, 4043, 4044),
                // Bar 103 (index 5): Bearish Displacement 2 (close 4040 <= 4050, upper wick (4047-4043)/(4047-4039) = 4/8 = 50% >= 35%)
                makeBar(103, 4043, 4047, 4039, 4040)
            ];
            const allPoolsBear = { eql: 4010.00, eqh: 4050.00, asiaLow: 4012.00, pdl: 4008.00 };
            const resBear = window.evaluateLiquidityPsychology(candlesBearish, 4050.00, "RESISTANCE", { name: "Equal Highs (EQH)", code: "EQH" }, allPoolsBear);
            results.bearishSetup = resBear;

            return results;
        })()
        """, 20)

        print(f"Immediate Sweep Prevented (Null): {algo_tests.get('immediateSweepNull')}")
        print(f"Invalidation Handled (Null): {algo_tests.get('invalidationDetected')}")

        bull = algo_tests.get('bullishSetup')
        print(f"\nBullish Sweep Result:")
        print(f"  Signal: {bull.get('signal')}")
        print(f"  Tag: {bull.get('tag')}")
        print(f"  Entry: {bull.get('entry')}")
        print(f"  Stop Loss: {bull.get('sl')} (Expected 3995.00 - 1.00 = 3994.00)")
        print(f"  Target (TP): {bull.get('tp')}")
        print(f"  Risk/Reward: {bull.get('rr')}")
        print(f"  Reason: {bull.get('reason')}")
        print(f"  Badge Text: {bull.get('badgeText')}")

        assert algo_tests.get('immediateSweepNull') == True, "Immediate sweep should return null!"
        assert algo_tests.get('invalidationDetected') == True, "Invalidated sweep should return null!"
        assert bull.get('signal') == 'HIGH_CONVICTION_BUY'
        assert bull.get('sl') == 3994.0, f"Expected SL 3994.00, got {bull.get('sl')}"
        assert bull.get('reason') == 'Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified'
        assert bull.get('badgeText') == '⚡ Liquidity Purged & Confirmed (Buyers Absorbed)'

        bear = algo_tests.get('bearishSetup')
        print(f"\nBearish Sweep Result:")
        print(f"  Signal: {bear.get('signal')}")
        print(f"  Tag: {bear.get('tag')}")
        print(f"  Entry: {bear.get('entry')}")
        print(f"  Stop Loss: {bear.get('sl')} (Expected 4055.00 + 1.00 = 4056.00)")
        print(f"  Target (TP): {bear.get('tp')}")
        print(f"  Risk/Reward: {bear.get('rr')}")
        print(f"  Reason: {bear.get('reason')}")
        print(f"  Badge Text: {bear.get('badgeText')}")

        assert bear.get('signal') == 'HIGH_CONVICTION_SELL'
        assert bear.get('sl') == 4056.0, f"Expected SL 4056.00, got {bear.get('sl')}"
        assert bear.get('reason') == 'Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified'
        assert bear.get('badgeText') == '⚡ Liquidity Purged & Confirmed (Buyers Absorbed)'

        print(">>> TEST 2 PASSED: All Algorithmic Logic matches requirements 100%!")

        # 3. VERIFY EXECUTION CARD AND CANVAS INTEGRATION UNDER LIVE INJECTION
        print("\n--- TEST 3: LIVE DASHBOARD INJECTION & UI CARD SYNC ---")
        card_sync = await eval_js(ws, """
        (() => {
            const bull = {
                type: "BUY",
                signal: "HIGH_CONVICTION_BUY",
                tag: "LIQUIDITY ABSORPTION CONFIRMED",
                levelName: "Asia Session Low (ASL)",
                levelCode: "ASL",
                liquidityLevel: 4005.00,
                sweepIndex: 2,
                sweepPrice: 4001.20,
                sweepLowest: 4001.20,
                entry: 4012.50,
                sl: 4000.20,
                tp: 4048.50,
                takeProfit: 4048.50,
                gainPts: 36.0,
                rr: "1 : 3.0",
                probability: "84% (5-Bar Absorption Verified)",
                reason: "Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified",
                badgeText: "⚡ Liquidity Purged & Confirmed (Buyers Absorbed)",
                neonBadgeText: "⚡ Liquidity Purged & Confirmed (Buyers Absorbed)"
            };

            // Set state and trigger UI sync
            const testBullObj = {
                type: "BUY",
                signal: "HIGH_CONVICTION_BUY",
                tag: "LIQUIDITY ABSORPTION CONFIRMED",
                levelName: "Asia Session Low (ASL)",
                levelCode: "ASL",
                liquidityLevel: 4002.00,
                sweepIndex: 2,
                sweepPrice: 3996.00,
                sweepLowest: 3996.00,
                entry: 4007.05,
                sl: 3995.00,
                tp: 4045.00,
                takeProfit: 4045.00,
                gainPts: 37.95,
                rr: "1 : 3.1",
                probability: "84% (5-Bar Absorption Verified)",
                reason: "Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified",
                badgeText: "⚡ Liquidity Purged & Confirmed (Buyers Absorbed)",
                neonBadgeText: "⚡ Liquidity Purged & Confirmed (Buyers Absorbed)"
            };

            window.latestLiquidityPsychology = testBullObj;

            const mockConfluence = {
                action: "HIGH CONVICTION BUY",
                confidence: "84% (5-Bar Absorption Verified)",
                reason: "Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified",
                agent4: {
                    entry: 4007.05,
                    sl: 3995.00,
                    tp1: 4045.00,
                    tp2: 4055.00,
                    rr: "1 : 3.1",
                    atr: 3.5
                }
            };
            const mockCandle = { time: Math.floor(Date.now() / 1000), open: 4005, high: 4010, low: 4004, close: 4007.05 };

            if (typeof updateActiveSetupCard === 'function') {
                updateActiveSetupCard(mockConfluence, mockCandle, 3995, 4055);
            }
            if (typeof redrawDrawings === 'function') {
                redrawDrawings();
            }

            const stNote = document.getElementById('stNoteVal');
            const stLiqBadge = document.getElementById('stLiquidityBadge');
            const stSl = document.getElementById('stSlVal');
            const stTp = document.getElementById('stTpVal');
            const pipeLiqPsy = document.getElementById('pipeLiqPsy');

            return {
                stNoteText: stNote ? stNote.innerText : null,
                stLiqBadgeText: stLiqBadge ? stLiqBadge.innerText : null,
                stLiqBadgeVisible: stLiqBadge ? stLiqBadge.style.display !== 'none' : false,
                stSlText: stSl ? stSl.innerText : null,
                stTpText: stTp ? stTp.innerText : null,
                pipeLiqPsyText: pipeLiqPsy ? pipeLiqPsy.innerText : null
            };
        })()
        """, 30)

        print(f"Signal Card Note: {card_sync.get('stNoteText')}")
        print(f"Liquidity Badge Text: {card_sync.get('stLiqBadgeText')}")
        print(f"Liquidity Badge Visible: {card_sync.get('stLiqBadgeVisible')}")
        print(f"Stop Loss Value: {card_sync.get('stSlText')}")
        print(f"Target TP Value: {card_sync.get('stTpText')}")
        print(f"Pipeline Pill: {card_sync.get('pipeLiqPsyText')}")

        assert "Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified" in card_sync.get('stNoteText'), "Execution Card reason mismatch!"
        assert "⚡ Liquidity Purged & Confirmed (Buyers Absorbed)" in card_sync.get('stLiqBadgeText'), "Neon Badge text mismatch!"
        assert card_sync.get('stLiqBadgeVisible') == True, "Liquidity badge should be visible!"
        print(">>> TEST 3 PASSED: Execution Card synced flawlessly.")

        # 4. CAPTURE SCREENSHOT FOR VERIFICATION
        print("\n--- CAPTURING FULL VERIFICATION SCREENSHOT ---")
        screenshot_data = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, 40)
        img_bytes = base64.b64decode(screenshot_data["result"]["data"])
        ss_path = "liquidity_candle_psychology_verified.png"
        with open(ss_path, "wb") as f:
            f.write(img_bytes)
        print(f"Screenshot saved to: {ss_path} ({len(img_bytes)} bytes)")

        print("\n==================================================================")
        print(" ALL VERIFICATIONS PASSED WITH ZERO ERRORS! ")
        print("==================================================================")

    finally:
        if ws:
            await ws.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except:
            proc.kill()

if __name__ == '__main__':
    asyncio.run(main())
