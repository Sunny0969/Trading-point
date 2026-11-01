import json
import os
import subprocess
import time
import urllib.request
import websocket
import sys
import base64

sys.stdout.reconfigure(encoding='utf-8')

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
REMOTE_PORT = 9232
TARGET_HTML = "D:/trading code try/gold_dashboard.html"

# Launch Headless Edge
cmd = [
    EDGE_PATH,
    f"--remote-debugging-port={REMOTE_PORT}",
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1600,1100",
    f"file:///{TARGET_HTML}"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(2.5)

try:
    url = f"http://127.0.0.1:{REMOTE_PORT}/json"
    req = urllib.request.urlopen(url)
    tabs = json.loads(req.read().decode('utf-8'))
    
    # Correctly find the gold_dashboard.html tab
    target_tab = None
    for t in tabs:
        if 'gold_dashboard' in t.get('url', '') or 'TradingPoint' in t.get('title', ''):
            target_tab = t
            break
            
    if not target_tab:
        raise RuntimeError(f"Could not find dashboard tab! Available: {[(t.get('title'), t.get('url')) for t in tabs]}")
        
    ws_url = target_tab['webSocketDebuggerUrl']
    print(f"Connected to Dashboard WebSocket: {ws_url} (Title: {target_tab.get('title')})")

    ws = websocket.create_connection(ws_url, timeout=15)

    msg_id = 0
    def cdp_send(method, params=None):
        global msg_id
        msg_id += 1
        payload = {"id": msg_id, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        while True:
            resp = json.loads(ws.recv())
            if resp.get('id') == msg_id:
                return resp.get('result', {})

    cdp_send("Runtime.enable")
    cdp_send("Page.enable")
    time.sleep(1.0)

    # 1. Setup authenticated session and switch to education view
    init_res = cdp_send("Runtime.evaluate", {
        "expression": """
        (function() {
            localStorage.setItem('tradingpoint_local_user', JSON.stringify({ email: 'suneel.pirkash@demo.com', name: 'Suneel Pirkash' }));
            if (typeof switchPortalView === 'function') {
                switchPortalView('education');
            }
            return {
                sidebarVisible: document.getElementById('traderAdminSidebar') ? window.getComputedStyle(document.getElementById('traderAdminSidebar')).display : 'none',
                eduNavExists: !!document.getElementById('adminNav_education'),
                eduNavActive: document.getElementById('adminNav_education') ? document.getElementById('adminNav_education').classList.contains('active') : false,
                eduViewDisplay: document.getElementById('view-education-portal') ? window.getComputedStyle(document.getElementById('view-education-portal')).display : 'none',
                hash: window.location.hash
            };
        })()
        """,
        "returnByValue": True
    })

    print("Education Navigation State:", json.dumps(init_res.get('result', {}).get('value', {}), indent=2))
    assert init_res['result']['value']['eduNavExists'] == True, "adminNav_education does not exist!"
    assert init_res['result']['value']['eduNavActive'] == True, "adminNav_education is not active!"
    assert init_res['result']['value']['eduViewDisplay'] == 'block', "view-education-portal is not display: block!"

    time.sleep(1.0)

    # 2. Check sticky TOC and Indicator Cards
    toc_res = cdp_send("Runtime.evaluate", {
        "expression": """
        (function() {
            var toc = document.querySelector('.edu-toc-sidebar');
            var tocLinks = Array.from(document.querySelectorAll('.edu-toc-link')).map(l => ({
                href: l.getAttribute('href'),
                text: l.innerText.trim(),
                active: l.classList.contains('active')
            }));

            var cards = Array.from(document.querySelectorAll('.edu-indicator-card')).map(c => ({
                id: c.id,
                title: c.querySelector('h2') ? c.querySelector('h2').innerText.trim() : '',
                category: c.getAttribute('data-category'),
                visible: window.getComputedStyle(c).display !== 'none'
            }));

            return {
                tocFound: !!toc,
                tocLinksCount: tocLinks.length,
                tocLinks: tocLinks,
                cardsCount: cards.length,
                cards: cards
            };
        })()
        """,
        "returnByValue": True
    })

    toc_data = toc_res.get('result', {}).get('value', {})
    print(f"TOC Links Count: {toc_data.get('tocLinksCount')}")
    print(f"Indicator Cards Count: {toc_data.get('cardsCount')}")

    assert toc_data.get('tocLinksCount') == 10, f"Expected 10 TOC links, got {toc_data.get('tocLinksCount')}"
    assert toc_data.get('cardsCount') == 10, f"Expected 10 cards, got {toc_data.get('cardsCount')}"

    # 3. Test Search Filter
    filter_res = cdp_send("Runtime.evaluate", {
        "expression": """
        (function() {
            var input = document.getElementById('eduSearchInput');
            input.value = 'FVG';
            filterEduCards('FVG');

            var visibleCards = Array.from(document.querySelectorAll('.edu-indicator-card')).filter(c => window.getComputedStyle(c).display !== 'none').map(c => c.id);

            // Reset search
            input.value = '';
            filterEduCards('');

            return {
                fvgMatches: visibleCards,
                totalAfterReset: Array.from(document.querySelectorAll('.edu-indicator-card')).filter(c => window.getComputedStyle(c).display !== 'none').length
            };
        })()
        """,
        "returnByValue": True
    })

    assert 'sec-smc-fvg' in filter_res['result']['value']['fvgMatches'], "sec-smc-fvg not in search matches!"
    assert filter_res['result']['value']['totalAfterReset'] == 10, "Reset did not restore 10 cards!"

    # 4. Take Screenshot of the Education Portal
    screen_res = cdp_send("Page.captureScreenshot", {"format": "png"})
    png_data = base64.b64decode(screen_res.get("data", ""))

    screenshot_path = "education_portal_verified.png"
    with open(screenshot_path, "wb") as f:
        f.write(png_data)
    print(f"Saved screenshot: {screenshot_path} ({len(png_data)} bytes)")

    print("✅ ALL TESTS PASSED SUCCESSFULLY 100%!")

finally:
    try: ws.close()
    except: pass
    proc.kill()
