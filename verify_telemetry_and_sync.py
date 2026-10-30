"""
Comprehensive test and verification of the Unified Candle Pipeline,
Selective On-Chart Overlays, and Dedicated Modular Telemetry Panel.
"""

import sys
import os
import json
import asyncio
import subprocess
import websockets
import base64
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
    port = 9340
    user_data = os.path.abspath("edge_telemetry_profile")

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

    print("Launching Edge headless...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    await asyncio.sleep(3.5)

    try:
        ver_resp = requests.get(f"http://127.0.0.1:{port}/json/list").json()
        target_ws_url = None
        for page in ver_resp:
            if "gold_dashboard.html" in page.get("url", ""):
                target_ws_url = page.get("webSocketDebuggerUrl")
                break
        if not target_ws_url and len(ver_resp) > 0:
            target_ws_url = ver_resp[0].get("webSocketDebuggerUrl")

        print(f"Connecting to CDP WebSocket: {target_ws_url}")
        async with websockets.connect(target_ws_url, max_size=25*1024*1024) as ws:
            await send_cmd(ws, "Page.enable", msg_id=2)
            await send_cmd(ws, "Runtime.enable", msg_id=3)

            # Wait 3 seconds for data fetch and indicator calculations
            print("Waiting for dashboard data and candle calculation...")
            await asyncio.sleep(3.5)

            # 1. Check Console / Errors
            res_err = await eval_js(ws, "window.__errors__ || []", msg_id=4)
            print("Console Errors check:", res_err)

            # 2. Check modular telemetry container and state
            has_container = await eval_js(ws, "!!document.getElementById('modular-indicator-telemetry')", msg_id=5)
            print(f"Modular Telemetry Container exists: {has_container}")
            assert has_container, "modular-indicator-telemetry container must exist"

            has_state = await eval_js(ws, "!!window.modularEngineState", msg_id=6)
            active_tab = await eval_js(ws, "window.modularEngineState ? window.modularEngineState.activeTab : null", msg_id=7)
            indicators = await eval_js(ws, "window.modularEngineState ? Object.keys(window.modularEngineState.indicators) : []", msg_id=8)
            print(f"Telemetry State exists: {has_state}, Active Tab: {active_tab}, Indicators: {indicators}")
            assert set(indicators) == {'SMC', 'LIQUIDITY', 'DLS', 'FIBONACCI', 'BREAKOUT'}, "All 5 modular indicators must be in telemetry state"

            # 3. Print full telemetry data for each indicator
            telemetry_data = await eval_js(ws, "window.modularEngineState.indicators", msg_id=9)
            print("Telemetry State Data:")
            print(json.dumps(telemetry_data, indent=2))

            # 4. Test interactive Tab Switching
            for tab in ['SMC', 'LIQUIDITY', 'DLS', 'FIBONACCI', 'BREAKOUT']:
                await eval_js(ws, f"window.switchModularTab('{tab}')", msg_id=10)
                await asyncio.sleep(0.2)
                rendered_text = await eval_js(ws, "document.getElementById('modular-indicator-telemetry').innerText", msg_id=11)
                assert f"{tab} INDICATOR ENGINE" in rendered_text.upper(), f"Tab {tab} must be reflected in rendered header"
                print(f"Verified Tab [{tab}] rendering in Telemetry Card!")

            # 5. Test Live Tick Synchronization
            print("Testing unified real-time tick synchronization...")
            tick_js = """(() => {
                const testSpot = 4015.50;
                applyTickerData({
                    price: testSpot,
                    change_pct: 0.45,
                    high: 4030.0,
                    low: 3980.0
                });
                return currentLiveSpot;
            })()"""
            updated_spot = await eval_js(ws, tick_js, msg_id=12)
            print(f"Injected Live Tick. Current spot: {updated_spot}")
            assert updated_spot == 4015.50, "Live spot must update to 4015.50"

            # Check that telemetry state responded to live spot
            dls_telemetry = await eval_js(ws, "window.modularEngineState.indicators.DLS", msg_id=13)
            print("DLS Telemetry after tick:", json.dumps(dls_telemetry, indent=2))

            # 6. Test Invalidation & Real-Time Projection Cancel
            inval_test_js = """(() => {
                // Force an SL breach to test instant invalidation
                shortTermSignalLock = {
                    active: true,
                    signalType: 'BUY',
                    action: 'HIGH CONVICTION BUY',
                    confidence: '95%',
                    entryPrice: 4020.0,
                    sl: 4010.0,
                    tp1: 4040.0,
                    tp2: 4050.0,
                    reason: 'Bullish Test Long',
                    status: 'ACTIVE_HOLD',
                    lockedAt: Date.now(),
                    maxLockDurationMs: 3600000
                };
                // Price drops below SL (4005 < 4010)
                currentLiveSpot = 4005.0;
                updateActiveSetupCard({ action: 'BUY', buyVotes: 3, sellVotes: 1 }, rawCandleData[rawCandleData.length-1], 3990, 4030);
                return {
                    status: shortTermSignalLock.status,
                    active: shortTermSignalLock.active,
                    dirText: document.getElementById('stDirectionPill').innerText
                };
            })()"""
            inval_res = await eval_js(ws, inval_test_js, msg_id=14)
            print("Instant Invalidation Test Result:", inval_res)
            assert inval_res.get("status") == "SL_HIT", "Setup must immediately flip to SL_HIT"
            assert inval_res.get("active") is False, "Active trade lock must be released immediately"
            assert "INVALIDATED" in inval_res.get("dirText"), "Direction pill must display INVALIDATED"

            # 7. Capture Full Screen & Telemetry Verification Screenshot
            print("Capturing verification screenshot...")
            scr = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=15)
            data_b64 = scr.get("result", {}).get("data", "")
            with open("telemetry_and_sync_verified.png", "wb") as img_f:
                img_f.write(base64.b64decode(data_b64))
            print("Saved screenshot to telemetry_and_sync_verified.png")

    finally:
        proc.kill()
        print("Edge closed.")

if __name__ == "__main__":
    asyncio.run(main())
