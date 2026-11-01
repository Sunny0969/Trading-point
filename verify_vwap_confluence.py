"""
Verification script for VWAP + EMA + FVG Confluence Engine
"""

import sys
import os
import json
import asyncio
import subprocess
import websockets
import requests

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
    return res.get("result", {}).get("result", {}).get("value")

async def main():
    html_path = os.path.abspath("gold_dashboard.html").replace("\\", "/")
    file_url = f"file:///{html_path}"
    port = 9345
    user_data = os.path.abspath("edge_vwap_profile")

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_bin):
        edge_bin = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    cmd = [
        edge_bin,
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-first-run",
        "--disable-background-networking",
        file_url
    ]

    print("Launching Edge Headless...")
    proc = subprocess.Popen(cmd)
    try:
        ws_url = None
        for _ in range(30):
            await asyncio.sleep(0.5)
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/json")
                pages = resp.json()
                for p in pages:
                    if p.get("type") == "page" and "gold_dashboard.html" in p.get("url", ""):
                        ws_url = p.get("webSocketDebuggerUrl")
                        break
                if not ws_url:
                    for p in pages:
                        if p.get("type") == "page":
                            ws_url = p.get("webSocketDebuggerUrl")
                            break
                if ws_url:
                    break
            except Exception:
                pass

        if not ws_url:
            print("FAILED: Could not obtain WebSocket URL from Edge")
            return False

        print(f"Connected to CDP WebSocket at {ws_url}")
        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            await send_cmd(ws, "Runtime.enable", msg_id=1)
            await send_cmd(ws, "Console.enable", msg_id=2)

            # Wait for dashboard to finish initial calculation
            await asyncio.sleep(3.5)

            # Test 1: Check UI Elements
            print("\n[TEST 1] Checking UI Elements and Toggles...")
            toggles_check = await eval_js(ws, """
                (() => {
                    const indToggle = document.getElementById('ind-toggle-vwapEmaFvg');
                    const modalToggle = document.getElementById('modal-toggle-vwapEmaFvg');
                    const pipe = document.getElementById('pipeVwapFvg');
                    return {
                        hasIndToggle: !!indToggle,
                        indChecked: indToggle ? indToggle.checked : false,
                        hasModalToggle: !!modalToggle,
                        modalChecked: modalToggle ? modalToggle.checked : false,
                        hasPipe: !!pipe,
                        pipeText: pipe ? pipe.innerText : ''
                    };
                })()
            """, 10)
            print("Toggles Check:", json.dumps(toggles_check, indent=2))
            assert toggles_check["hasIndToggle"], "Dropdown toggle ind-toggle-vwapEmaFvg missing"
            assert toggles_check["hasModalToggle"], "Modal toggle modal-toggle-vwapEmaFvg missing"
            assert toggles_check["hasPipe"], "Pipeline badge pipeVwapFvg missing"
            print("  --> PASS: UI Elements exist and initialized")

            # Test 2: Check Config & State Variables
            print("\n[TEST 2] Checking Config & State Variables...")
            config_check = await eval_js(ws, """
                (() => {
                    return {
                        defaultConfig: DEFAULT_INDICATOR_CONFIG.vwapEmaFvg,
                        weight: MODULE_WEIGHTS.vwapEmaFvg,
                        indicatorSetting: indicatorSettings.vwapEmaFvg,
                        globalActive: window.vwap_ema_fvg_active,
                        hasFunctionSeries: typeof calculateSessionVWAPSeries === 'function',
                        hasFunctionVWAP: typeof calculateSessionVWAP === 'function',
                        hasFunctionEval: typeof evaluateVWAP_EMA_FVG === 'function',
                        hasFunctionDraw: typeof drawVWAP_EMA_FVG_Overlay === 'function'
                    };
                })()
            """, 11)
            print("Config Check:", json.dumps(config_check, indent=2))
            assert config_check["weight"] == 20, f"Expected weight 20, got {config_check['weight']}"
            assert config_check["hasFunctionVWAP"], "calculateSessionVWAP missing"
            assert config_check["hasFunctionEval"], "evaluateVWAP_EMA_FVG missing"
            assert config_check["hasFunctionDraw"], "drawVWAP_EMA_FVG_Overlay missing"
            print("  --> PASS: Indicator functions and configurations are verified")

            # Test 3: Session VWAP Calculation & 00:00 UTC Reset
            print("\n[TEST 3] Testing Session VWAP & UTC Daily Reset Routine...")
            vwap_calc_check = await eval_js(ws, """
                (() => {
                    // Create 4 bars spanning two different UTC days
                    // Day 1: 2026-10-31 23:30, 23:45
                    // Day 2: 2026-11-01 00:00, 00:15
                    const t1 = 1793489400; // 2026-10-31 23:30 UTC
                    const t2 = 1793490300; // 2026-10-31 23:45 UTC
                    const t3 = 1793491200; // 2026-11-01 00:00 UTC (Reset day)
                    const t4 = 1793492100; // 2026-11-01 00:15 UTC

                    const testCandles = [
                        { time: t1, open: 2700, high: 2710, low: 2695, close: 2705, volume: 1000 },
                        { time: t2, open: 2705, high: 2715, low: 2700, close: 2710, volume: 1000 },
                        { time: t3, open: 4000, high: 4010, low: 3995, close: 4005, volume: 500 }, // Huge price jump next day
                        { time: t4, open: 4005, high: 4015, low: 4000, close: 4010, volume: 500 }
                    ];

                    const series = calculateSessionVWAPSeries(testCandles);
                    const curVWAP = calculateSessionVWAP(testCandles);

                    return {
                        bar1_vwap: series[0].value,
                        bar2_vwap: series[1].value,
                        bar3_vwap: series[2].value, // Must reset to ~4003.33, NOT dragged by 2700s
                        bar4_vwap: series[3].value,
                        curVWAP: curVWAP
                    };
                })()
            """, 12)
            print("VWAP Calc Check:", json.dumps(vwap_calc_check, indent=2))
            assert vwap_calc_check["bar3_vwap"] > 3900, "VWAP did not reset at 00:00 UTC daily session boundary!"
            print("  --> PASS: Session VWAP correctly resets at 00:00 UTC session start")

            # Test 4: Bullish Confluence Mitigation (BUY) Trigger
            print("\n[TEST 4] Testing Bullish Confluence Mitigation Setup (BUY)...")
            bull_check = await eval_js(ws, """
                (() => {
                    const now = Math.floor(Date.now() / 1000);
                    const candles = [];
                    let p = 4000;
                    for (let i = 0; i < 20; i++) {
                        candles.push({
                            time: now - (25 - i) * 900,
                            open: p,
                            high: p + 3,
                            low: p - 1,
                            close: p + 2,
                            volume: 500
                        });
                        p += 1.5;
                    }
                    // EMA 20 is around 4023, VWAP is around 4020
                    // FVG aligns within 3.50 USD of EMA 20: [4022.00, 4024.00], eqLevel: 4023.00
                    const fvg = { type: 'BULLISH_FVG', bottom: 4022.00, top: 4024.00, eqLevel: 4023.00, time: now - 3600 };

                    // Bar 22: Price pulls back into FVG
                    candles.push({
                        time: now - 1800,
                        open: 4028,
                        high: 4029,
                        low: 4022.5, // Dips into FVG
                        close: 4024.5,
                        volume: 600
                    });

                    // Bar 23: Rejection candle with lower wick >= 35% closing above VWAP
                    candles.push({
                        time: now - 900,
                        open: 4025,
                        high: 4028.5,
                        low: 4022.0, // lower wick = 4025 - 4022 = 3.0. Range = 4028.5 - 4022 = 6.5 (46.1% wick)
                        close: 4027.5,
                        volume: 800
                    });

                    // Current Bar:
                    candles.push({
                        time: now,
                        open: 4027.5,
                        high: 4030.0,
                        low: 4026.5,
                        close: 4029.0,
                        volume: 750
                    });

                    const res = evaluateVWAP_EMA_FVG(candles, [fvg], 4029.0);
                    return res;
                })()
            """, 13)
            print("Bullish Setup Check:", json.dumps(bull_check, indent=2))
            assert bull_check is not None, "Bullish setup returned null"
            assert bull_check["active"] == True, "Bullish setup should be active"
            assert bull_check["direction"] == "BUY", "Bullish setup direction should be BUY"
            assert "1 : 2.5" in bull_check["rr"], "Risk-to-Reward should be 1:2.5"
            print("  --> PASS: Bullish Confluence Mitigation (BUY) verified with 1:2.5 RR")

            # Test 5: Bearish Confluence Mitigation (SELL) Trigger
            print("\n[TEST 5] Testing Bearish Confluence Mitigation Setup (SELL)...")
            bear_check = await eval_js(ws, """
                (() => {
                    const now = Math.floor(Date.now() / 1000);
                    const candles = [];
                    let p = 4050;
                    for (let i = 0; i < 20; i++) {
                        candles.push({
                            time: now - (25 - i) * 900,
                            open: p,
                            high: p + 1,
                            low: p - 3,
                            close: p - 2,
                            volume: 500
                        });
                        p -= 1.5;
                    }
                    // EMA 20 is around 4027, VWAP is around 4030
                    // FVG aligns within 3.50 USD of EMA 20: [4025.00, 4027.00], eqLevel: 4026.00
                    const fvg = { type: 'BEARISH_FVG', bottom: 4025.00, top: 4027.00, eqLevel: 4026.00, time: now - 3600 };

                    // Bar 22: Pulls back up into FVG
                    candles.push({
                        time: now - 1800,
                        open: 4022,
                        high: 4026.5, // Touches FVG
                        low: 4021,
                        close: 4024.5,
                        volume: 600
                    });

                    // Bar 23: Rejection candle with upper wick >= 35% closing below VWAP
                    candles.push({
                        time: now - 900,
                        open: 4024,
                        high: 4027.5, // upper wick = 4027.5 - 4024 = 3.5. Range = 4027.5 - 4021 = 6.5 (53.8% wick)
                        low: 4021,
                        close: 4022.5,
                        volume: 800
                    });

                    // Current Bar:
                    candles.push({
                        time: now,
                        open: 4022.5,
                        high: 4023.5,
                        low: 4019.5,
                        close: 4020.0,
                        volume: 750
                    });

                    const res = evaluateVWAP_EMA_FVG(candles, [fvg], 4020.0);
                    return res;
                })()
            """, 14)
            print("Bearish Setup Check:", json.dumps(bear_check, indent=2))
            assert bear_check is not None, "Bearish setup returned null"
            assert bear_check["active"] == True, "Bearish setup should be active"
            assert bear_check["direction"] == "SELL", "Bearish setup direction should be SELL"
            assert "1 : 2.5" in bear_check["rr"], "Risk-to-Reward should be 1:2.5"
            print("  --> PASS: Bearish Confluence Mitigation (SELL) verified with 1:2.5 RR")

            # Test 6: Chop & Entanglement Filter (STANDBY)
            print("\n[TEST 6] Testing Chop & Entanglement Filter...")
            chop_check = await eval_js(ws, """
                (() => {
                    const now = Math.floor(Date.now() / 1000);
                    // Price hovering flatly right around VWAP, EMA entangled
                    const candles = [];
                    for (let i = 0; i < 25; i++) {
                        const flip = (i % 2 === 0) ? 4010.2 : 4009.8;
                        candles.push({
                            time: now - (25 - i) * 900,
                            open: 4010,
                            high: 4010.5,
                            low: 4009.5,
                            close: flip,
                            volume: 400
                        });
                    }
                    return evaluateVWAP_EMA_FVG(candles, [], 4010);
                })()
            """, 15)
            print("Chop Check:", json.dumps(chop_check, indent=2))
            assert chop_check["isChopStandby"] == True or chop_check["status"] == "CHOP FILTERED", "Chop filter did not trigger on entangled candles"
            print("  --> PASS: Chop & Entanglement Filter correctly puts engine in STANDBY")

            # Test 7: Modular Telemetry Switch to VWAP_FVG Tab
            print("\n[TEST 7] Testing Modular Telemetry UI Tab Switch...")
            tab_check = await eval_js(ws, """
                (() => {
                    switchModularTab('VWAP_FVG');
                    const container = document.getElementById('modular-indicator-telemetry');
                    return {
                        activeTab: modularEngineState.activeTab,
                        htmlSnippet: container ? container.innerHTML : ''
                    };
                })()
            """, 16)
            assert tab_check["activeTab"] == "VWAP_FVG", "Modular telemetry tab did not switch to VWAP_FVG"
            assert "VWAP + FVG" in tab_check["htmlSnippet"], "VWAP + FVG heading not found in telemetry panel"
            print("  --> PASS: Telemetry panel cleanly switched to VWAP+FVG tab")

            # Test 8: Canvas Overlay Drawing Execution
            print("\n[TEST 8] Testing Canvas Overlay Drawing Routine...")
            draw_check = await eval_js(ws, """
                (() => {
                    try {
                        const cvs = document.getElementById('drawingCanvas');
                        const ctx = cvs.getContext('2d');
                        drawVWAP_EMA_FVG_Overlay(ctx, window.latestVWAP_EMA_FVG, rawCandleData);
                        return { ok: true };
                    } catch (e) {
                        return { ok: false, error: e.toString() };
                    }
                })()
            """, 17)
            print("Draw Check:", json.dumps(draw_check, indent=2))
            assert draw_check["ok"], f"drawVWAP_EMA_FVG_Overlay threw error: {draw_check.get('error')}"
            print("  --> PASS: Canvas overlay draws cleanly without errors")

            print("\n==========================================")
            print("ALL 8 VERIFICATION TESTS PASSED SUCCESSFULLY (100% GREEN)")
            print("==========================================")
            return True

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass

if __name__ == '__main__':
    ok = asyncio.run(main())
    if not ok:
        sys.exit(1)
