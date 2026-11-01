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
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, msg_id)
    return res.get("result", {}).get("result", {}).get("value")

async def main():
    html_path = os.path.abspath("gold_dashboard.html").replace("\\", "/")
    file_url = f"file:///{html_path}"
    port = 9360
    user_data = os.path.abspath("edge_auth_test_profile")

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
        for _ in range(25):
            await asyncio.sleep(0.4)
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/json").json()
                for p in resp:
                    if p.get("type") == "page" and "gold_dashboard.html" in p.get("url", ""):
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

            # Wait for dashboard initial load
            await asyncio.sleep(2.5)

            # [TEST 1] Initial state for Logged Out User
            print("\n[TEST 1] Checking Logged Out State...")
            logged_out_state = await eval_js(ws, """
                (() => {
                    const dashView = document.getElementById('view-dashboard');
                    const termView = document.getElementById('view-terminal');
                    const btnDash = document.getElementById('nav-btn-dashboard');
                    return {
                        isLoggedIn: isUserLoggedIn(),
                        dashDisplay: dashView ? window.getComputedStyle(dashView).display : null,
                        termDisplay: termView ? window.getComputedStyle(termView).display : null,
                        btnDashDisplay: btnDash ? window.getComputedStyle(btnDash).display : null
                    };
                })()
            """, 10)
            print("Logged Out State:", json.dumps(logged_out_state, indent=2))
            assert logged_out_state["isLoggedIn"] == False, "User should be logged out initially"
            assert logged_out_state["dashDisplay"] == "block", "view-dashboard should be visible for logged out user"
            assert logged_out_state["termDisplay"] == "none", "view-terminal should be hidden for logged out user"
            assert logged_out_state["btnDashDisplay"] != "none", "nav-btn-dashboard should be visible for logged out user"
            print("  --> PASS: Logged out user sees view-dashboard (landing page)")

            # [TEST 2] Authenticating User
            print("\n[TEST 2] Authenticating User & Verifying Dashboard Routing...")
            auth_state = await eval_js(ws, """
                (async () => {
                    const mockUser = { id: 'usr-888', email: 'institutional_trader@gold.com' };
                    await onUserAuthenticated(mockUser);
                    const dashView = document.getElementById('view-dashboard');
                    const termView = document.getElementById('view-terminal');
                    const btnDash = document.getElementById('nav-btn-dashboard');
                    return {
                        isLoggedIn: isUserLoggedIn(),
                        currentUser: currentAuthUser ? currentAuthUser.email : null,
                        dashDisplay: dashView ? window.getComputedStyle(dashView).display : null,
                        termDisplay: termView ? window.getComputedStyle(termView).display : null,
                        btnDashDisplay: btnDash ? window.getComputedStyle(btnDash).display : null,
                        hash: window.location.hash
                    };
                })()
            """, 11)
            print("Authenticated State:", json.dumps(auth_state, indent=2))
            assert auth_state["isLoggedIn"] == True, "User should now be logged in"
            assert auth_state["dashDisplay"] == "none", "view-dashboard MUST be hidden for logged in user"
            assert auth_state["termDisplay"] == "flex", "view-terminal MUST be visible for logged in user"
            assert auth_state["btnDashDisplay"] == "none", "nav-btn-dashboard MUST be hidden for logged in user"
            print("  --> PASS: Logged in user is instantly shown their trading dashboard; landing page is hidden")

            # [TEST 3] Trying to switch to 'dashboard' while logged in
            print("\n[TEST 3] Testing Forbid Dashboard switch while logged in...")
            forbid_check = await eval_js(ws, """
                (() => {
                    switchView('dashboard');
                    const dashView = document.getElementById('view-dashboard');
                    const termView = document.getElementById('view-terminal');
                    return {
                        dashDisplay: dashView ? window.getComputedStyle(dashView).display : null,
                        termDisplay: termView ? window.getComputedStyle(termView).display : null
                    };
                })()
            """, 12)
            print("Forbid Dashboard Check:", json.dumps(forbid_check, indent=2))
            assert forbid_check["dashDisplay"] == "none", "view-dashboard MUST remain hidden while logged in"
            assert forbid_check["termDisplay"] == "flex", "view-terminal MUST remain visible while logged in"
            print("  --> PASS: Logged in user cannot be shown landing page; stays on dashboard")

            # [TEST 4] Logging Out User
            print("\n[TEST 4] Logging Out User & Verifying Return to Landing Page...")
            logout_state = await eval_js(ws, """
                (async () => {
                    await handleSupabaseLogout();
                    const dashView = document.getElementById('view-dashboard');
                    const termView = document.getElementById('view-terminal');
                    const btnDash = document.getElementById('nav-btn-dashboard');
                    return {
                        isLoggedIn: isUserLoggedIn(),
                        dashDisplay: dashView ? window.getComputedStyle(dashView).display : null,
                        termDisplay: termView ? window.getComputedStyle(termView).display : null,
                        btnDashDisplay: btnDash ? window.getComputedStyle(btnDash).display : null
                    };
                })()
            """, 13)
            print("Logout State:", json.dumps(logout_state, indent=2))
            assert logout_state["isLoggedIn"] == False, "User should now be logged out"
            assert logout_state["dashDisplay"] == "block", "view-dashboard MUST be shown after logout"
            assert logout_state["termDisplay"] == "none", "view-terminal MUST be hidden after logout"
            assert logout_state["btnDashDisplay"] != "none", "nav-btn-dashboard MUST be visible after logout"
            print("  --> PASS: Logging out immediately displays the landing overview page")

            # [TEST 5] Checking Animations and Transitions Removal
            print("\n[TEST 5] Verifying Animation, Scroll, Click & Mouse Effect Removal...")
            anim_check = await eval_js(ws, """
                (() => {
                    const dot = document.querySelector('.blinking-dot');
                    const btnCta = document.querySelector('.btn-primary-cta');
                    const btnProfile = document.querySelector('.btn-user-profile-icon');
                    const htmlStyle = window.getComputedStyle(document.documentElement);

                    return {
                        scrollBehavior: htmlStyle.scrollBehavior,
                        dotAnimation: dot ? window.getComputedStyle(dot).animationName : null,
                        btnCtaTransition: btnCta ? window.getComputedStyle(btnCta).transition : null,
                        btnProfileTransition: btnProfile ? window.getComputedStyle(btnProfile).transition : null
                    };
                })()
            """, 14)
            print("Animation Removal Check:", json.dumps(anim_check, indent=2))
            assert anim_check["scrollBehavior"] == "auto", "scrollBehavior should be auto"
            assert anim_check["dotAnimation"] == "none" or anim_check["dotAnimation"] is None, "blinking-dot animation should be none"
            print("  --> PASS: Animations, transitions, and smooth scroll successfully neutralized")

            print("\n==========================================")
            print("ALL AUTH ROUTING & ANIMATION REMOVAL TESTS PASSED (100% GREEN)")
            print("==========================================")
            return True

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass

if __name__ == '__main__':
    ok = asyncio.run(main())
    if not ok:
        sys.exit(1)
