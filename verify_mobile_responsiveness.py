"""
Comprehensive Automated Verification for TradingView & Exness Mobile Responsiveness
Using Python CDP & Microsoft Edge Headless (390x844 iPhone Viewport)
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

def check_html_file(filepath):
    print(f"\n--- Checking Static HTML Requirements in {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        "Viewport Meta Tag": 'content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"',
        "Mobile Bottom Nav": 'id="mobileBottomNav"',
        "Mobile Tab Chart": 'data-tab="chart"',
        "Mobile Tab Trade": 'data-tab="execution"',
        "Mobile Tab Signals": 'data-tab="signals"',
        "Mobile Tab Wallet": 'data-tab="wallet"',
        "Mobile Bottom Sheet Container": 'id="mobileSheetContainer"',
        "Mobile Execution Panel": 'id="mPanelExecution"',
        "Mobile Signals Panel": 'id="mPanelSignals"',
        "Mobile Wallet Panel": 'id="mPanelWallet"',
        "Mobile Timeframe Pill Bar": 'id="mobileTfPillRow"',
        "Lightweight Charts Touch Handling": 'vertTouchDrag: true'
    }

    all_passed = True
    for name, query in checks.items():
        if query in content:
            print(f" [PASS] {name}")
        else:
            print(f" [FAIL] {name}")
            all_passed = False

    return all_passed

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

async def run_cdp_mobile_test():
    print("\n--- Running Edge Headless Mobile Viewport CDP Test (390x844) ---")
    user_data = os.path.abspath('edge_fresh_user_data_mobile')
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9245",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--window-size=390,844",
        "file:///D:/trading code try/gold_dashboard.html#terminal"
    ])

    try:
        ws_url = None
        for _ in range(25):
            try:
                tabs = requests.get('http://127.0.0.1:9245/json').json()
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

        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            print("[x] Connected to Edge CDP on mobile viewport!")
            await send_cmd(ws, "Runtime.enable")
            await send_cmd(ws, "Page.enable")

            # Emulate iPhone device metrics
            await send_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": 390,
                "height": 844,
                "deviceScaleFactor": 3.0,
                "mobile": True,
                "fitWindow": True
            })

            await asyncio.sleep(2.5)

            # 1. Test Viewport and Mobile Layout State
            test1_js = """
            (function() {
                const termView = document.getElementById('view-terminal');
                const bottomNav = document.getElementById('mobileBottomNav');
                const chartEl = document.getElementById('chart');
                const sidebar = document.querySelector('.terminal-sidebar');
                const leftToolbar = document.querySelector('.tv-left-toolbar');
                const tfRow = document.getElementById('mobileTfPillRow');

                const termRect = termView ? termView.getBoundingClientRect() : null;
                const navRect = bottomNav ? bottomNav.getBoundingClientRect() : null;
                const chartRect = chartEl ? chartEl.getBoundingClientRect() : null;

                const navComputedDisplay = bottomNav ? window.getComputedStyle(bottomNav).display : null;
                const sidebarComputedDisplay = sidebar ? window.getComputedStyle(sidebar).display : null;
                const leftToolbarDisplay = leftToolbar ? window.getComputedStyle(leftToolbar).display : null;

                return {
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight,
                    termWidth: termRect ? termRect.width : 0,
                    termHeight: termRect ? termRect.height : 0,
                    bottomNavVisible: navComputedDisplay === 'flex',
                    bottomNavHeight: navRect ? navRect.height : 0,
                    chartWidth: chartRect ? chartRect.width : 0,
                    chartHeight: chartRect ? chartRect.height : 0,
                    desktopSidebarHidden: sidebarComputedDisplay === 'none',
                    leftToolbarHidden: leftToolbarDisplay === 'none',
                    mobileTfPillRowVisible: tfRow ? window.getComputedStyle(tfRow).display !== 'none' : false
                };
            })()
            """
            res1 = await send_cmd(ws, "Runtime.evaluate", {"expression": test1_js, "returnByValue": True}, msg_id=10)
            metrics = res1.get("result", {}).get("result", {}).get("value")
            print("\n>>> 1. MOBILE VIEWPORT & LAYOUT METRICS:")
            print(json.dumps(metrics, indent=2))

            # 2. Test Mobile Tab Switching: Open Execution Sheet
            test2_js = """
            (function() {
                switchMobileTab('execution');
                const container = document.getElementById('mobileSheetContainer');
                const execPanel = document.getElementById('mPanelExecution');
                const isContainerActive = container ? container.classList.contains('active') : false;
                const buyBtn = document.querySelector('.m-btn-buy');
                const sellBtn = document.querySelector('.m-btn-sell');
                const lotInput = document.getElementById('mDemoLotInput');

                return {
                    sheetActive: isContainerActive,
                    execPanelVisible: execPanel ? execPanel.style.display !== 'none' : false,
                    buyBtnHeight: buyBtn ? buyBtn.getBoundingClientRect().height : 0,
                    sellBtnHeight: sellBtn ? sellBtn.getBoundingClientRect().height : 0,
                    lotInputHeight: lotInput ? lotInput.getBoundingClientRect().height : 0
                };
            })()
            """
            res2 = await send_cmd(ws, "Runtime.evaluate", {"expression": test2_js, "returnByValue": True}, msg_id=20)
            exec_metrics = res2.get("result", {}).get("result", {}).get("value")
            print("\n>>> 2. MOBILE EXECUTION SHEET & TOUCH TARGETS:")
            print(json.dumps(exec_metrics, indent=2))

            # Capture screenshot of Mobile Execution Sheet
            res_shot1 = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=25)
            img1 = res_shot1.get("result", {}).get("data")
            if img1:
                with open("mobile_execution_sheet_verified.png", "wb") as f:
                    f.write(base64.b64decode(img1))
                print(" [x] Captured mobile_execution_sheet_verified.png")

            # 3. Test Mobile Tab Switching: Signals Sheet & Wallet Sheet
            test3_js = """
            (function() {
                switchMobileTab('signals');
                const sigPanel = document.getElementById('mPanelSignals');
                const hasSignalsContent = sigPanel ? sigPanel.innerHTML.length > 50 : false;

                switchMobileTab('wallet');
                const walPanel = document.getElementById('mPanelWallet');
                const balEl = document.getElementById('mWalletBalance');

                // Return to chart
                switchMobileTab('chart');

                return {
                    hasSignalsContent: hasSignalsContent,
                    walletBalance: balEl ? balEl.innerText : null
                };
            })()
            """
            res3 = await send_cmd(ws, "Runtime.evaluate", {"expression": test3_js, "returnByValue": True}, msg_id=30)
            sig_metrics = res3.get("result", {}).get("result", {}).get("value")
            print("\n>>> 3. MOBILE SIGNALS & WALLET SHEETS TEST:")
            print(json.dumps(sig_metrics, indent=2))

            # 4. Capture Full-Screen Mobile Chart view
            await asyncio.sleep(0.5)
            res_shot2 = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=40)
            img2 = res_shot2.get("result", {}).get("data")
            if img2:
                with open("mobile_tradingview_exness_verified.png", "wb") as f:
                    f.write(base64.b64decode(img2))
                print(" [x] Captured mobile_tradingview_exness_verified.png")

            return True

    finally:
        proc.terminate()
        proc.wait()
        print("Edge CDP cleanly closed.")

def main():
    passed = True
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        p = check_html_file(fn)
        if not p:
            passed = False

    if passed:
        print("\nAll static HTML checks passed! Starting CDP headless mobile verification...")
        asyncio.run(run_cdp_mobile_test())
    else:
        print("\n[ERROR] Some static checks failed!")

if __name__ == '__main__':
    main()
