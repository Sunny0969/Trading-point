import subprocess
import asyncio
import json
import base64
import os
import sys
import requests
import websockets

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

async def main():
    user_data = os.path.abspath('edge_fresh_user_data_liquidity_engine')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    print("Launching Edge headless...")
    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9231",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--window-size=1600,1000",
        "file:///d:/trading code try/gold_dashboard.html#terminal"
    ])

    try:
        ws_url = None
        for _ in range(25):
            try:
                tabs = requests.get('http://127.0.0.1:9231/json').json()
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
            print("Failed to find gold_dashboard tab!")
            return

        async with websockets.connect(ws_url, max_size=15*1024*1024) as ws:
            print("Connected to WebSocket CDP!")
            await send_cmd(ws, "Runtime.enable")
            await send_cmd(ws, "Page.enable")
            await send_cmd(ws, "Page.reload")
            
            end_t = asyncio.get_event_loop().time() + 4.0
            while asyncio.get_event_loop().time() < end_t:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    msg = json.loads(raw)
                    if msg.get("method") == "Runtime.exceptionThrown":
                        print("\n>>> PAGE RUNTIME EXCEPTION:")
                        print(json.dumps(msg["params"]["exceptionDetails"], indent=2))
                except asyncio.TimeoutError:
                    pass

            # 1. Test trackInstitutionalLiquidity function
            test1_code = """
            (function() {
                try {
                    const nowSec = Math.floor(Date.now() / 1000);
                    const mockCandles = [];
                    for (let i = 80; i >= 0; i--) {
                        const t = nowSec - (i * 900);
                        mockCandles.push({
                            time: t,
                            open: 4040.0 + Math.sin(i * 0.2) * 15,
                            high: 4055.0 + Math.sin(i * 0.2) * 15,
                            low: 4030.0 + Math.sin(i * 0.2) * 15,
                            close: 4045.0 + Math.sin(i * 0.2) * 15,
                            volume: 1200
                        });
                    }
                    mockCandles[60].high = 4075.25;
                    mockCandles[65].high = 4075.40;

                    const pools = trackInstitutionalLiquidity(mockCandles);
                    return pools;
                } catch (e) {
                    return { error: e.toString() };
                }
            })()
            """
            res1 = await send_cmd(ws, "Runtime.evaluate", {"expression": test1_code, "returnByValue": True}, msg_id=10)
            print("\n>>> 1. TRACK INSTITUTIONAL LIQUIDITY RESULT:")
            val1 = res1.get("result", {}).get("result", {}).get("value")
            print(json.dumps(val1, indent=2))

            # 2. Test detectInstitutionalLiquiditySweeps with Bullish Sweep of Asia Low (ASL)
            test2_code = """
            (function() {
                try {
                    const pools = {
                        asiaHigh: 4078.50,
                        asiaLow: 4042.00,
                        londonHigh: 4085.00,
                        londonLow: 4040.00,
                        pdh: 4095.00,
                        pdl: 4035.00,
                        eqh: 4088.00,
                        eql: 4042.20
                    };

                    const mockCandles = [
                        { time: 1000, open: 4048, high: 4050, low: 4044, close: 4046, volume: 1000 },
                        { time: 1900, open: 4046, high: 4047, low: 4041, close: 4043, volume: 1200 },
                        { time: 2800, open: 4043, high: 4048, low: 4040, close: 4044, volume: 1500 },
                        { time: 3700, open: 4044, high: 4046, low: 4041, close: 4042.5, volume: 1800 },
                        { time: 4600, open: 4042.00, high: 4046.00, low: 4038.00, close: 4045.50, volume: 3500 }
                    ];

                    const sweepRes = detectInstitutionalLiquiditySweeps(mockCandles, pools);
                    window.latestLiquiditySweep = sweepRes;

                    const mockConfluence = {
                        action: 'INSTITUTIONAL BUY TRIGGERED',
                        buyVotes: 5.0,
                        sellVotes: 0.0,
                        agent4: { atr: 4.0, sl: sweepRes.sl, tp1: sweepRes.tp, entry: sweepRes.entry }
                    };
                    updateActiveSetupCard(mockConfluence, mockCandles[4], 4035.0, 4085.0);

                    return {
                        sweepType: sweepRes.type,
                        verdict: sweepRes.verdict,
                        levelName: sweepRes.levelName,
                        sweptPrice: sweepRes.sweptPrice,
                        entry: sweepRes.entry,
                        sl: sweepRes.sl,
                        tp: sweepRes.tp,
                        badgeText: sweepRes.badgeText,
                        cardBadgeText: document.getElementById('stLiquidityBadge')?.innerText,
                        cardBadgeDisplay: document.getElementById('stLiquidityBadge')?.style.display,
                        cardDirPill: document.getElementById('stDirectionPill')?.innerText,
                        cardTpVal: document.getElementById('stTpVal')?.innerText
                    };
                } catch (e) {
                    return { error: e.toString(), stack: e.stack, typeVar: typeof shortTermSignalLock, typeWin: typeof window.shortTermSignalLock };
                }
            })()
            """
            res2 = await send_cmd(ws, "Runtime.evaluate", {"expression": test2_code, "returnByValue": True}, msg_id=20)
            print("\n>>> 2. BULLISH LIQUIDITY SWEEP & EXECUTION CARD TEST:")
            val2 = res2.get("result", {}).get("result", {}).get("value")
            print(json.dumps(val2, indent=2))

            # 3. Test Liquidity Shield
            test3_code = """
            (function() {
                try {
                    const pools = {
                        asiaHigh: 4080.00,
                        asiaLow: 4040.00,
                        eqh: 4075.00,
                        eql: 4042.00
                    };
                    const shieldBuy = applyLiquidityShield('BUY', 4043.0, pools);
                    const shieldSell = applyLiquidityShield('SELL', 4074.0, pools);
                    return {
                        shieldBuyAllowed: shieldBuy.allowed,
                        shieldBuyReason: shieldBuy.reason,
                        shieldSellAllowed: shieldSell.allowed,
                        shieldSellReason: shieldSell.reason
                    };
                } catch (e) {
                    return { error: e.toString() };
                }
            })()
            """
            res3 = await send_cmd(ws, "Runtime.evaluate", {"expression": test3_code, "returnByValue": True}, msg_id=30)
            print("\n>>> 3. LIQUIDITY SHIELD TEST:")
            val3 = res3.get("result", {}).get("result", {}).get("value")
            print(json.dumps(val3, indent=2))

            # 4. Capture screenshot
            res4 = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=40)
            img_data = res4.get("result", {}).get("data")
            if img_data:
                with open("liquidity_engine_verified.png", "wb") as f:
                    f.write(base64.b64decode(img_data))
                print("\n>>> Screenshot saved to liquidity_engine_verified.png (bytes:", len(img_data), ")")

    finally:
        proc.terminate()
        proc.wait()
        print("Edge cleanly terminated.")

if __name__ == '__main__':
    asyncio.run(main())
