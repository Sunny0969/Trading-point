"""
Comprehensive test and verification of the Daily Liquidity Sniper (1D Sweep + 1M Trigger) Engine
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
    port = 9335
    user_data = os.path.abspath("edge_dls_test_profile")

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
            await asyncio.sleep(3)

            # 1. Check Console / Errors
            res_err = await eval_js(ws, "window.__errors__ || []", msg_id=4)
            print("Console Errors check:", res_err)

            # 2. Check toggle existence & initial active state
            has_toggle = await eval_js(ws, "!!document.getElementById('ind-toggle-dailyLiquiditySniper')", msg_id=5)
            is_checked = await eval_js(ws, "document.getElementById('ind-toggle-dailyLiquiditySniper') ? document.getElementById('ind-toggle-dailyLiquiditySniper').checked : false", msg_id=6)
            is_active_mem = await eval_js(ws, "!!window.daily_liquidity_sniper_active", msg_id=7)
            dls_setting = await eval_js(ws, "!!(window.indicatorSettings && window.indicatorSettings.dailyLiquiditySniper)", msg_id=8)
            print(f"Toggle exists: {has_toggle}, isChecked: {is_checked}, memory active: {is_active_mem}, setting: {dls_setting}")

            # 3. Check evaluateDailyLiquiditySniper existence & state
            eval_fn_type = await eval_js(ws, "typeof window.evaluateDailyLiquiditySniper", msg_id=9)
            print("evaluateDailyLiquiditySniper type:", eval_fn_type)

            latest_dls = await eval_js(ws, "window.latestDailyLiquiditySniper", msg_id=10)
            print("Current window.latestDailyLiquiditySniper:", json.dumps(latest_dls, indent=2))

            # 4. Check Execution Signals Card DOM elements
            st_dir = await eval_js(ws, "document.getElementById('stDirectionPill') ? document.getElementById('stDirectionPill').innerText : ''", msg_id=11)
            st_action = await eval_js(ws, "document.getElementById('stSignalAction') ? document.getElementById('stSignalAction').innerText : ''", msg_id=12)
            st_badge = await eval_js(ws, "document.getElementById('stLiquidityBadge') ? document.getElementById('stLiquidityBadge').innerText : ''", msg_id=13)
            st_pipe = await eval_js(ws, "document.getElementById('pipeDLS') ? document.getElementById('pipeDLS').innerText : ''", msg_id=14)
            st_entry = await eval_js(ws, "document.getElementById('stEntryVal') ? document.getElementById('stEntryVal').innerText : ''", msg_id=15)
            st_sl = await eval_js(ws, "document.getElementById('stSlVal') ? document.getElementById('stSlVal').innerText : ''", msg_id=16)
            st_tp = await eval_js(ws, "document.getElementById('stTpVal') ? document.getElementById('stTpVal').innerText : ''", msg_id=17)
            st_note = await eval_js(ws, "document.getElementById('stNoteVal') ? document.getElementById('stNoteVal').innerText : ''", msg_id=18)

            print(f"Card Pill Direction: {st_dir}")
            print(f"Card Action: {st_action}")
            print(f"Card Liquidity Badge: {st_badge}")
            print(f"Pipeline Pill: {st_pipe}")
            print(f"Card Entry: {st_entry}, SL: {st_sl}, TP: {st_tp}")
            print(f"Card Setup Reason / Note: {st_note}")

            # 5. Algorithmic Simulation of SHORT Trigger:
            # Price sweeps PDH ($4030.00), solid red candle closes with high $4032.00, close $4029.00, low $4028.50, next candle low breaks $4028.50 to $4027.00
            sim_short_js = """(() => {
                const pdh = 4030.0;
                const pdl = 3980.0;
                const mock1M = [
                    { time: 820, open: 4022.0, high: 4024.0, low: 4021.0, close: 4023.0 },
                    { time: 880, open: 4023.0, high: 4025.0, low: 4022.0, close: 4024.5 },
                    { time: 940, open: 4024.5, high: 4026.0, low: 4023.5, close: 4025.0 },
                    { time: 1000, open: 4025.0, high: 4028.0, low: 4024.0, close: 4027.0 },
                    { time: 1060, open: 4027.0, high: 4029.0, low: 4026.0, close: 4028.5 },
                    // Sweep bar: high 4032.0 > pdh, solid red candle close 4029.20 < open 4031.50
                    { time: 1120, open: 4031.5, high: 4032.0, low: 4028.8, close: 4029.2 },
                    // Trigger bar: low 4027.5 < red candle low 4028.8, close 4028.0
                    { time: 1180, open: 4029.2, high: 4029.5, low: 4027.5, close: 4028.0 }
                ];
                const res = window.evaluateDailyLiquiditySniper(mock1M, { pdh, pdl }, 4028.0);
                return res;
            })()"""
            sim_short_res = await eval_js(ws, sim_short_js, msg_id=19)
            print("Simulated SHORT Trigger Test Result:")
            print(json.dumps(sim_short_res, indent=2))
            assert sim_short_res.get("direction") == "SELL", "Expected SELL direction for PDH sweep breakout"
            assert sim_short_res.get("sl") == 4032.50, "Expected SL = red candle high + 0.50 USD ($4032.50)"
            assert "PDH Swept + 1M Red Candle Low Purged" in sim_short_res.get("reason"), "Expected correct reason string"

            # 6. Algorithmic Simulation of BUY Trigger:
            # Price pierces PDL ($3980.00), solid green candle closes with low $3978.00, close $3981.00, high $3981.50, next candle breaks high to $3983.00
            sim_buy_js = """(() => {
                const pdh = 4030.0;
                const pdl = 3980.0;
                const mock1M = [
                    { time: 820, open: 3989.0, high: 3990.0, low: 3986.0, close: 3987.0 },
                    { time: 880, open: 3987.0, high: 3988.0, low: 3985.0, close: 3986.0 },
                    { time: 940, open: 3986.0, high: 3987.0, low: 3984.0, close: 3985.0 },
                    { time: 1000, open: 3985.0, high: 3986.0, low: 3982.0, close: 3983.0 },
                    { time: 1060, open: 3983.0, high: 3984.0, low: 3981.0, close: 3981.5 },
                    // Sweep bar: low 3977.5 < pdl, solid green candle close 3980.80 > open 3978.20
                    { time: 1120, open: 3978.2, high: 3981.2, low: 3977.5, close: 3980.8 },
                    // Trigger bar: high 3982.5 > green candle high 3981.2, close 3982.0
                    { time: 1180, open: 3980.8, high: 3982.5, low: 3980.5, close: 3982.0 }
                ];
                const res = window.evaluateDailyLiquiditySniper(mock1M, { pdh, pdl }, 3982.0);
                return res;
            })()"""
            sim_buy_res = await eval_js(ws, sim_buy_js, msg_id=20)
            print("Simulated BUY Trigger Test Result:")
            print(json.dumps(sim_buy_res, indent=2))
            assert sim_buy_res.get("direction") == "BUY", "Expected BUY direction for PDL sweep breakout"
            assert sim_buy_res.get("sl") == 3977.00, "Expected SL = green candle low - 0.50 USD ($3977.00)"
            assert "PDL Swept + 1M Green Candle High Purged" in sim_buy_res.get("reason"), "Expected correct reason string"

            # 7. Test UI Card Live Update with Simulated Short Setup around current spot (3922)
            inject_short_card = """(() => {
                const pdh = 3925.0;
                const pdl = 3890.0;
                const mock1M = [
                    { time: 820, open: 3920.0, high: 3922.0, low: 3919.0, close: 3921.0 },
                    { time: 880, open: 3921.0, high: 3923.0, low: 3920.0, close: 3922.5 },
                    { time: 940, open: 3922.5, high: 3924.0, low: 3921.5, close: 3923.0 },
                    { time: 1000, open: 3923.0, high: 3924.5, low: 3922.0, close: 3924.0 },
                    { time: 1060, open: 3924.0, high: 3925.5, low: 3923.0, close: 3924.5 },
                    // Sweep bar: high 3926.0 > pdh, solid red candle close 3923.20 < open 3925.50
                    { time: 1120, open: 3925.5, high: 3926.0, low: 3922.8, close: 3923.2 },
                    // Trigger bar: low 3921.5 < red candle low 3922.8, close 3922.0
                    { time: 1180, open: 3923.2, high: 3923.5, low: 3921.5, close: 3922.0 }
                ];
                const res = window.evaluateDailyLiquiditySniper(mock1M, { pdh, pdl }, 3922.0);
                window.latestDailyLiquiditySniper = res;
                window.updateActiveSetupCard(window.activeModularConfluence, mock1M[mock1M.length-1], 3890, 3925);
                return true;
            })()"""
            await eval_js(ws, inject_short_card, msg_id=21)
            await asyncio.sleep(0.5)

            card_dir_short = await eval_js(ws, "document.getElementById('stDirectionPill').innerText", msg_id=22)
            card_badge_short = await eval_js(ws, "document.getElementById('stLiquidityBadge').innerText", msg_id=23)
            card_sl_short = await eval_js(ws, "document.getElementById('stSlVal').innerText", msg_id=24)
            card_note_short = await eval_js(ws, "document.getElementById('stNoteVal').innerText", msg_id=25)

            print("Verified Live Card State after DLS Short Trigger:")
            print(f"-> Direction Pill: {card_dir_short}")
            print(f"-> Liquidity Badge: {card_badge_short}")
            print(f"-> Stop Loss: {card_sl_short}")
            print(f"-> Setup Note: {card_note_short}")
            assert card_dir_short == "SELL", f"Expected SELL, got {card_dir_short}"
            assert "DLS-1M SNIPER" in card_badge_short, "Badge should show DLS-1M SNIPER"
            assert "$3926.50" in card_sl_short, "Card SL should show $3926.50 (red high + 0.50)"

            # 8. Capture high-res screenshot
            print("Capturing verification screenshot...")
            scr = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=26)
            data_b64 = scr.get("result", {}).get("data", "")
            with open("daily_liquidity_sniper_verified.png", "wb") as img_f:
                img_f.write(base64.b64decode(data_b64))
            print("Saved screenshot to daily_liquidity_sniper_verified.png")

    finally:
        proc.kill()
        print("Edge closed.")

if __name__ == "__main__":
    asyncio.run(main())
