import sys
import os
import json
import asyncio
import subprocess
import websockets
import requests
import shutil

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
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id)
    if "exceptionDetails" in res.get("result", {}):
        print("[EXCEPTION IN JS]:", json.dumps(res["result"]["exceptionDetails"], indent=2))
    return res.get("result", {}).get("result", {}).get("value")

async def main():
    html_path = os.path.abspath("gold_dashboard.html").replace("\\", "/")
    file_url = f"file:///{html_path}"
    port = 9385
    user_data = os.path.abspath("edge_portal_test_profile")

    if os.path.exists(user_data):
        shutil.rmtree(user_data, ignore_errors=True)

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    proc = subprocess.Popen([
        edge_bin,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--disable-background-networking",
        file_url
    ])

    try:
        ws_url = None
        for _ in range(30):
            await asyncio.sleep(0.5)
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/json")
                pages = resp.json()
                for p in pages:
                    if p.get("type") == "page":
                        ws_url = p.get("webSocketDebuggerUrl")
                        print(f"Found page target: {p.get('title')} ({p.get('url')})")
                        break
                if ws_url:
                    break
            except Exception:
                pass

        if not ws_url:
            print("FAILED: Could not find page target")
            return

        print(f"[CDP] Connected to Edge target page: {ws_url}")

        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            await send_cmd(ws, "Runtime.enable", msg_id=1)
            await send_cmd(ws, "Console.enable", msg_id=2)

            # Wait for dashboard to finish initial script parsing and DOM readiness
            await asyncio.sleep(3.5)

            # Step 1: Initial state (Logged out)
            print("\n--- STEP 1: VERIFYING INITIAL LOGGED OUT STATE ---")
            init_state = await eval_js(ws, """(() => {
                const isPortalActive = document.body.classList.contains('portal-mode-active');
                const sidebar = document.getElementById('traderAdminSidebar');
                const sidebarDisplay = sidebar ? window.getComputedStyle(sidebar).display : 'null';
                const dashView = document.getElementById('view-dashboard');
                const dashDisplay = dashView ? window.getComputedStyle(dashView).display : 'null';
                const traderDashView = document.getElementById('view-trader-dashboard');
                const traderDashDisplay = traderDashView ? window.getComputedStyle(traderDashView).display : 'null';
                const navbar = document.querySelector('.navbar');
                const navbarDisplay = navbar ? window.getComputedStyle(navbar).display : 'null';
                return {
                    url: window.location.href,
                    title: document.title,
                    isPortalActive,
                    sidebarDisplay,
                    dashDisplay,
                    traderDashDisplay,
                    navbarDisplay
                };
            })()""", msg_id=20)
            print("Initial State:", json.dumps(init_state, indent=2))
            assert init_state["isPortalActive"] == False, "portal-mode-active should be False initially"
            assert init_state["sidebarDisplay"] == "none", "Sidebar should be hidden initially"
            assert init_state["traderDashDisplay"] == "none", "Trader dashboard should be hidden initially"
            assert init_state["dashDisplay"] == "block", "Public landing page should be visible initially"
            assert init_state["navbarDisplay"] != "none", "Public top navbar should be visible initially"
            print("[PASS] Initial logged-out state is 100% correct!")

            # Step 2: Simulate User Login
            print("\n--- STEP 2: SIMULATING USER LOGIN ---")
            login_state = await eval_js(ws, """(async () => {
                // Call onUserAuthenticated with simulated user
                await onUserAuthenticated({
                    id: 'usr_abc_789',
                    email: 'trader.pro@firm.com'
                });
                
                await new Promise(r => setTimeout(r, 200));

                const isPortalActive = document.body.classList.contains('portal-mode-active');
                const sidebar = document.getElementById('traderAdminSidebar');
                const sidebarDisplay = sidebar ? window.getComputedStyle(sidebar).display : 'null';
                const traderDashView = document.getElementById('view-trader-dashboard');
                const traderDashDisplay = traderDashView ? window.getComputedStyle(traderDashView).display : 'null';
                const dashView = document.getElementById('view-dashboard');
                const dashDisplay = dashView ? window.getComputedStyle(dashView).display : 'null';
                const navbar = document.querySelector('.navbar');
                const navbarDisplay = navbar ? window.getComputedStyle(navbar).display : 'null';

                const sidebarUserName = document.getElementById('sidebarUserName')?.innerText;
                const sidebarUserEmail = document.getElementById('sidebarUserEmail')?.innerText;
                const activeNav = document.querySelector('.admin-nav-item.active')?.id;
                const dynamicEquity = document.getElementById('dashDynamicEquity')?.innerText;

                return {
                    isPortalActive,
                    sidebarDisplay,
                    traderDashDisplay,
                    dashDisplay,
                    navbarDisplay,
                    sidebarUserName,
                    sidebarUserEmail,
                    activeNav,
                    dynamicEquity,
                    hash: window.location.hash
                };
            })()""", msg_id=30)
            print("Post-Login State:", json.dumps(login_state, indent=2))
            assert login_state["isPortalActive"] == True, "portal-mode-active MUST be True upon login"
            assert login_state["sidebarDisplay"] == "flex", "Left sidebar MUST be flex/visible upon login"
            assert login_state["traderDashDisplay"] == "block", "Trader Performance Dashboard MUST be block/visible upon login"
            assert login_state["dashDisplay"] == "none", "Public landing page MUST be hidden upon login"
            assert login_state["navbarDisplay"] == "none", "Public top navbar MUST be hidden in portal mode"
            assert login_state["activeNav"] == "adminNav_dashboard", "Active nav item MUST be adminNav_dashboard"
            assert "Trader.pro" in login_state["sidebarUserName"], f"Sidebar user name mismatch: {login_state['sidebarUserName']}"
            assert login_state["sidebarUserEmail"] == "trader.pro@firm.com", "Sidebar email mismatch"
            print("[PASS] Login routing to Trader Admin Dashboard with Left Sidebar verified!")

            # Step 3: Test Sidebar Navigation within Portal
            print("\n--- STEP 3: TESTING PORTAL NAVIGATION VIA LEFT SIDEBAR ---")
            
            # Navigate to Live Trade Terminal
            nav_trade = await eval_js(ws, """(() => {
                switchPortalView('trade');
                const termView = document.getElementById('view-terminal');
                const traderDashView = document.getElementById('view-trader-dashboard');
                const sidebar = document.getElementById('traderAdminSidebar');
                return {
                    termDisplay: window.getComputedStyle(termView).display,
                    traderDashDisplay: window.getComputedStyle(traderDashView).display,
                    sidebarDisplay: window.getComputedStyle(sidebar).display,
                    activeNav: document.querySelector('.admin-nav-item.active')?.id,
                    hash: window.location.hash
                };
            })()""", msg_id=40)
            print("Trade Nav State:", json.dumps(nav_trade, indent=2))
            assert nav_trade["termDisplay"] == "flex", "Terminal view should be flex"
            assert nav_trade["traderDashDisplay"] == "none", "Trader dashboard should be hidden"
            assert nav_trade["sidebarDisplay"] == "flex", "Sidebar MUST remain visible"
            assert nav_trade["activeNav"] == "adminNav_trade"
            print("[PASS] Navigation to Live Trade Terminal verified!")

            # Navigate to Signals Portal
            nav_signals = await eval_js(ws, """(() => {
                switchPortalView('signals');
                const sigView = document.getElementById('view-signals-portal');
                const termView = document.getElementById('view-terminal');
                const sidebar = document.getElementById('traderAdminSidebar');
                return {
                    sigDisplay: window.getComputedStyle(sigView).display,
                    termDisplay: window.getComputedStyle(termView).display,
                    sidebarDisplay: window.getComputedStyle(sidebar).display,
                    activeNav: document.querySelector('.admin-nav-item.active')?.id,
                    hash: window.location.hash
                };
            })()""", msg_id=50)
            print("Signals Nav State:", json.dumps(nav_signals, indent=2))
            assert nav_signals["sigDisplay"] == "block", "Signals view should be block"
            assert nav_signals["sidebarDisplay"] == "flex", "Sidebar MUST remain visible"
            assert nav_signals["activeNav"] == "adminNav_signals"
            print("[PASS] Navigation to Signals Portal verified!")

            # Navigate to Wallet Portal
            nav_wallet = await eval_js(ws, """(() => {
                switchPortalView('wallet');
                const walView = document.getElementById('view-wallet-portal');
                const sidebar = document.getElementById('traderAdminSidebar');
                return {
                    walDisplay: window.getComputedStyle(walView).display,
                    sidebarDisplay: window.getComputedStyle(sidebar).display,
                    activeNav: document.querySelector('.admin-nav-item.active')?.id,
                    hash: window.location.hash
                };
            })()""", msg_id=60)
            print("Wallet Nav State:", json.dumps(nav_wallet, indent=2))
            assert nav_wallet["walDisplay"] == "block", "Wallet view should be block"
            assert nav_wallet["sidebarDisplay"] == "flex", "Sidebar MUST remain visible"
            assert nav_wallet["activeNav"] == "adminNav_wallet"
            print("[PASS] Navigation to Wallet Portal verified!")

            # Navigate back to Trader Dashboard
            nav_dash = await eval_js(ws, """(() => {
                switchPortalView('dashboard');
                const traderDashView = document.getElementById('view-trader-dashboard');
                const sidebar = document.getElementById('traderAdminSidebar');
                return {
                    traderDashDisplay: window.getComputedStyle(traderDashView).display,
                    sidebarDisplay: window.getComputedStyle(sidebar).display,
                    activeNav: document.querySelector('.admin-nav-item.active')?.id,
                    hash: window.location.hash
                };
            })()""", msg_id=70)
            print("Dashboard Nav State:", json.dumps(nav_dash, indent=2))
            assert nav_dash["traderDashDisplay"] == "block", "Trader dashboard should be block"
            assert nav_dash["sidebarDisplay"] == "flex", "Sidebar MUST remain visible"
            assert nav_dash["activeNav"] == "adminNav_dashboard"
            print("[PASS] Navigation back to Trader Dashboard verified!")

            # Step 4: Simulate User Logout
            print("\n--- STEP 4: SIMULATING USER LOGOUT ---")
            logout_state = await eval_js(ws, """(async () => {
                await handleSupabaseLogout();
                await new Promise(r => setTimeout(r, 100));

                const isPortalActive = document.body.classList.contains('portal-mode-active');
                const sidebar = document.getElementById('traderAdminSidebar');
                const sidebarDisplay = sidebar ? window.getComputedStyle(sidebar).display : 'null';
                const traderDashView = document.getElementById('view-trader-dashboard');
                const traderDashDisplay = traderDashView ? window.getComputedStyle(traderDashView).display : 'null';
                const dashView = document.getElementById('view-dashboard');
                const dashDisplay = dashView ? window.getComputedStyle(dashView).display : 'null';
                const navbar = document.querySelector('.navbar');
                const navbarDisplay = navbar ? window.getComputedStyle(navbar).display : 'null';
                const localUser = localStorage.getItem('tradingpoint_local_user');

                return {
                    isPortalActive,
                    sidebarDisplay,
                    traderDashDisplay,
                    dashDisplay,
                    navbarDisplay,
                    localUser
                };
            })()""", msg_id=80)
            print("Post-Logout State:", json.dumps(logout_state, indent=2))
            assert logout_state["isPortalActive"] == False, "portal-mode-active MUST be False after logout"
            assert logout_state["sidebarDisplay"] == "none", "Sidebar MUST be hidden after logout"
            assert logout_state["traderDashDisplay"] == "none", "Trader dashboard MUST be hidden after logout"
            assert logout_state["dashDisplay"] == "block", "Public landing page MUST be visible after logout"
            assert logout_state["navbarDisplay"] != "none", "Navbar MUST be visible after logout"
            assert logout_state["localUser"] is None, "Local user storage MUST be cleared after logout"
            print("[PASS] Logout routing back to public landing page verified!")

            print("\n========================================================")
            print("ALL ADMIN PORTAL & LOGOUT ROUTING TESTS PASSED (100% SUCCESS)!")
            print("========================================================")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()
        if os.path.exists(user_data):
            shutil.rmtree(user_data, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(main())
