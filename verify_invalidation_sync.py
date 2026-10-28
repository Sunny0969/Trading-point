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
    user_data = os.path.abspath('edge_fresh_user_data_invalidation_2')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    print("Launching Edge headless...")
    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9228",
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
                tabs = requests.get('http://127.0.0.1:9228/json').json()
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
            await asyncio.sleep(3.0)

            # 1. Trigger SL_HIT
            step1_code = """
            (function() {
                window.shortTermSignalLock.active = true;
                window.shortTermSignalLock.status = 'ACTIVE_HOLD';
                window.shortTermSignalLock.signalType = 'BUY';
                window.shortTermSignalLock.entryPrice = 4048.0;
                window.shortTermSignalLock.sl = 4045.0;
                window.shortTermSignalLock.tp1 = 4056.0;
                window.shortTermSignalLock.lockedAt = Date.now();
                window.shortTermSignalLock.confidence = '90% (INSTITUTIONAL SMC)';

                const mockCandle = { open: 4047.0, high: 4048.0, low: 4043.5, close: 4044.0, volume: 1500 };
                window.currentLiveSpot = 4044.0;
                const mockConfluence = { buyVotes: 1.0, sellVotes: 3.5, agent4: { atr: 3.0 } };

                updateActiveSetupCard(mockConfluence, mockCandle, 4040.0, 4060.0);

                return {
                    status: window.shortTermSignalLock.status,
                    active: window.shortTermSignalLock.active,
                    dirPill: document.getElementById('stDirPill')?.innerText,
                    confPill: document.getElementById('stConfPill')?.innerText,
                    note: document.getElementById('stNoteVal')?.innerText,
                    timer: document.getElementById('stLockTimer')?.innerText
                };
            })()
            """
            res1 = await send_cmd(ws, "Runtime.evaluate", {"expression": step1_code, "returnByValue": True}, msg_id=10)
            print("\n>>> 1. IMMEDIATELY AFTER SL BREACH:")
            print(json.dumps(res1.get("result", {}).get("result", {}).get("value"), indent=2))

            # 2. Fast forward time by 4 seconds to test auto-transition to NEXT signal
            step2_code = """
            (function() {
                // Simulate 4 seconds elapsed since invalidation
                window.shortTermSignalLock.completedAt = Date.now() - 4000;
                const mockCandle = { open: 4044.0, high: 4044.5, low: 4036.0, close: 4037.0, volume: 1800 };
                window.currentLiveSpot = 4037.0;
                const mockConfluence = { buyVotes: 0.5, sellVotes: 3.8, agent4: { atr: 3.0 } };

                updateActiveSetupCard(mockConfluence, mockCandle, 4030.0, 4055.0);

                return {
                    newStatus: window.shortTermSignalLock.status,
                    newActive: window.shortTermSignalLock.active,
                    newSignalType: window.shortTermSignalLock.signalType,
                    newAction: window.shortTermSignalLock.action,
                    newEntry: window.shortTermSignalLock.entryPrice,
                    newTp1: window.shortTermSignalLock.tp1,
                    newSl: window.shortTermSignalLock.sl,
                    newRr: window.shortTermSignalLock.rrText,
                    newReason: window.shortTermSignalLock.reason,
                    dirPill: document.getElementById('stDirPill')?.innerText,
                    confPill: document.getElementById('stConfPill')?.innerText,
                    timer: document.getElementById('stLockTimer')?.innerText
                };
            })()
            """
            res2 = await send_cmd(ws, "Runtime.evaluate", {"expression": step2_code, "returnByValue": True}, msg_id=20)
            print("\n>>> 2. AUTO-TRANSITION TO NEXT SIGNAL (AFTER 4 SECONDS):")
            print(json.dumps(res2.get("result", {}).get("result", {}).get("value"), indent=2))

            # 3. Test Long Term Swing Invalidation & Auto-Transition
            lt_code = """
            (function() {
                // Setup Bullish swing at 4040 with Invalidation at 4010
                window.longTermSignalLock.active = true;
                window.longTermSignalLock.status = 'ACTIVE_HOLD';
                window.longTermSignalLock.bias = 'BULLISH';
                window.longTermSignalLock.inval = 4010.0;
                window.longTermSignalLock.tp = 4090.0;
                window.longTermSignalLock.lockedAt = Date.now();

                // Breach inval with spot at 4005
                window.currentLiveSpot = 4005.0;
                const mockCandle = { open: 4012.0, high: 4012.0, low: 4004.0, close: 4005.0, volume: 1500 };
                const mockConfluence = { buyVotes: 0.5, sellVotes: 3.5, agent4: { atr: 3.5 } };
                
                updateActiveSetupCard(mockConfluence, mockCandle, 3990.0, 4050.0);
                const stoppedState = {
                    status: window.longTermSignalLock.status,
                    active: window.longTermSignalLock.active,
                    dirPill: document.getElementById('ltDirPill')?.innerText,
                    timer: document.getElementById('ltLockTimer')?.innerText,
                    action: document.getElementById('ltSignalAction')?.innerText
                };

                // Fast forward 5 seconds to test swing auto-transition
                window.longTermSignalLock.completedAt = Date.now() - 5000;
                updateActiveSetupCard(mockConfluence, mockCandle, 3990.0, 4050.0);
                const nextSwingState = {
                    newStatus: window.longTermSignalLock.status,
                    newBias: window.longTermSignalLock.bias,
                    newAction: window.longTermSignalLock.action,
                    newTp: window.longTermSignalLock.tp,
                    newInval: window.longTermSignalLock.inval,
                    newReason: window.longTermSignalLock.reason,
                    dirPill: document.getElementById('ltDirPill')?.innerText
                };

                return { stoppedState, nextSwingState };
            })()
            """
            res3 = await send_cmd(ws, "Runtime.evaluate", {"expression": lt_code, "returnByValue": True}, msg_id=30)
            print("\n>>> 3. LONG-TERM SWING INVALIDATION & NEXT SWING TRANSITION:")
            print(json.dumps(res3.get("result", {}).get("result", {}).get("value"), indent=2))

    finally:
        proc.terminate()
        proc.wait()
        print("Edge cleanly terminated.")

if __name__ == '__main__':
    asyncio.run(main())
