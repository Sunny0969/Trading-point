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
    user_data = os.path.abspath('edge_fresh_user_data_breakout')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    print("Launching Edge headless...")
    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9226",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--window-size=1600,1000",
        "file:///d:/trading code try/gold_dashboard.html#terminal"
    ])

    try:
        ws_url = None
        for _ in range(20):
            try:
                tabs = requests.get('http://127.0.0.1:9226/json').json()
                for t in tabs:
                    if 'gold_dashboard' in t.get('url', ''):
                        ws_url = t['webSocketDebuggerUrl']
                        print("Found gold tab:", t['url'])
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
            # Wait 4 seconds for charts and breakout logic to process
            await asyncio.sleep(4.0)

            # 1. Check window.activeBreakoutSetup
            res1 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": "JSON.stringify(window.activeBreakoutSetup)"
            }, msg_id=10)
            val1 = res1.get("result", {}).get("result", {}).get("value")
            print("\n>>> ACTIVE BREAKOUT SETUP (JSON):")
            print(val1)

            # 2. Check Breakout Tab switch
            res2 = await send_cmd(ws, "Runtime.evaluate", {
                "expression": "switchSignalTab('breakout'); document.getElementById('tabContentBreakout').innerText"
            }, msg_id=20)
            val2 = res2.get("result", {}).get("result", {}).get("value")
            print("\n>>> TAB CONTENT BREAKOUT TEXT:")
            print(val2)

            # 3. Capture screenshot
            res4 = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=40)
            img_data = res4.get("result", {}).get("data")
            if img_data:
                with open("breakout_terminal_verified.png", "wb") as f:
                    f.write(base64.b64decode(img_data))
                print("\n>>> Screenshot successfully saved to breakout_terminal_verified.png (bytes:", len(img_data), ")")

    finally:
        proc.terminate()
        proc.wait()
        print("Edge cleanly terminated.")

if __name__ == '__main__':
    asyncio.run(main())
