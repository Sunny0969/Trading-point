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
    user_data = os.path.abspath('edge_fresh_user_data_agile_sync')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    print("Launching Edge headless...")
    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9229",
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
                tabs = requests.get('http://127.0.0.1:9229/json').json()
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

        async with websockets.connect(ws_url) as ws:
            print("Connected to WebSocket CDP!")
            await asyncio.sleep(3.5)

            # 1. Verify Initial Card Badge & Target Sync
            check1_code = """
            (function() {
                const timerText = document.getElementById('stLockTimer')?.innerText;
                const tpValText = document.getElementById('stTpVal')?.innerText;
                const entryValText = document.getElementById('stEntryVal')?.innerText;
                const dirPillText = document.getElementById('stDirectionPill')?.innerText;
                return { timerText, tpValText, entryValText, dirPillText, lock: window.shortTermSignalLock };
            })()
            """
            res1 = await send_cmd(ws, "Runtime.evaluate", {"expression": check1_code, "returnByValue": True}, msg_id=10)
            print("\n>>> 1. INITIAL AGILE SCANNER & CARD STATE:")
            print(json.dumps(res1.get("result", {}).get("result", {}).get("value"), indent=2))

            # 2. Test Ghost Candle Target Sync with Signal Card
            # Simulate a candle pattern that projects target to 4118.70
            check2_code = """
            (function() {
                // Mock candle pattern with netTargetPush to 4118.7
                window.currentCandlePattern = {
                    pattern: 'Bullish Expansion Marubozu',
                    bias: 'BULLISH',
                    netTargetPush: 48.74,
                    hasVolSurge: true
                };

                const mockLastCandle = {
                    time: Math.floor(Date.now() / 1000),
                    open: 4068.0,
                    high: 4072.0,
                    low: 4067.0,
                    close: 4069.96,
                    volume: 2500
                };

                const mockConfluence = {
                    action: 'HIGH CONVICTION BUY',
                    buyVotes: 4.5,
                    sellVotes: 0.5,
                    agent4: { atr: 4.5, tp1: 4118.70, sl: 4066.96, entry: 4069.96 }
                };

                // Run generateNext3CandlesPrediction
                generateNext3CandlesPrediction(mockLastCandle, 4059.0, 4042.0, 4078.0, [mockLastCandle], mockConfluence);

                // Run updateActiveSetupCard
                updateActiveSetupCard(mockConfluence, mockLastCandle, 4042.0, 4078.0);

                return {
                    ghostTargetLabel: window.ghostPredictionTargetLabel || 'Calculated in series',
                    cardTpVal: document.getElementById('stTpVal')?.innerText,
                    cardEntryVal: document.getElementById('stEntryVal')?.innerText,
                    cardRrVal: document.getElementById('stRrVal')?.innerText,
                    timerBadge: document.getElementById('stLockTimer')?.innerText,
                    lockTp1: window.shortTermSignalLock.tp1
                };
            })()
            """
            res2 = await send_cmd(ws, "Runtime.evaluate", {"expression": check2_code, "returnByValue": True}, msg_id=20)
            print("\n>>> 2. GHOST PREDICTION TO SIGNAL CARD SYNCHRONIZATION TEST:")
            print(json.dumps(res2.get("result", {}).get("result", {}).get("value"), indent=2))

            # 3. Test Dynamic Expansion Runner when Spot reaches 4119.97 (The FOMC Spike)
            check3_code = """
            (function() {
                // Live spot rockets to 4119.97 (blowing past 4081.96)
                window.currentLiveSpot = 4119.97;
                const mockCandle = {
                    time: Math.floor(Date.now() / 1000),
                    open: 4070.0,
                    high: 4121.0,
                    low: 4068.0,
                    close: 4119.97,
                    volume: 4800
                };
                const mockConfluence = {
                    action: 'HIGH CONVICTION BUY',
                    buyVotes: 4.5,
                    sellVotes: 0.0,
                    agent4: { atr: 5.0, tp1: 4118.70, sl: 4066.96, entry: 4069.96 }
                };

                // Update card at spot 4119.97
                updateActiveSetupCard(mockConfluence, mockCandle, 4042.0, 4078.0);

                return {
                    status: window.shortTermSignalLock.status,
                    action: window.shortTermSignalLock.action,
                    entry: window.shortTermSignalLock.entryPrice,
                    sl: window.shortTermSignalLock.sl,
                    tp1: window.shortTermSignalLock.tp1,
                    cardSlText: document.getElementById('stSlVal')?.innerText,
                    cardTpText: document.getElementById('stTpVal')?.innerText,
                    timerText: document.getElementById('stLockTimer')?.innerText,
                    noteText: document.getElementById('stNoteVal')?.innerText
                };
            })()
            """
            res3 = await send_cmd(ws, "Runtime.evaluate", {"expression": check3_code, "returnByValue": True}, msg_id=30)
            print("\n>>> 3. EXPANSION RUNNER & BREAKEVEN SL TEST (FOMC ROCKET CANDLE):")
            print(json.dumps(res3.get("result", {}).get("result", {}).get("value"), indent=2))

            # 4. Capture screenshot
            res4 = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=40)
            img_data = res4.get("result", {}).get("data")
            if img_data:
                with open("ghost_agile_verified.png", "wb") as f:
                    f.write(base64.b64decode(img_data))
                print("\n>>> Screenshot saved to ghost_agile_verified.png (bytes:", len(img_data), ")")

    finally:
        proc.terminate()
        proc.wait()
        print("Edge cleanly terminated.")

if __name__ == '__main__':
    asyncio.run(main())
