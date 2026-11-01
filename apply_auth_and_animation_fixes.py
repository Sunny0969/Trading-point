import sys
import os
import hashlib

def main():
    print("Reading gold_dashboard.html...")
    with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Early SwitchView script
    target_early = '''    // ==========================================
    // INSTANT GLOBAL VIEW SWITCHER & ROUTER (EARLY LOAD)
    // ==========================================
    function switchView(viewName) {
      var dashView = document.getElementById('view-dashboard');
      var termView = document.getElementById('view-terminal');
      var btnDash = document.getElementById('nav-btn-dashboard');
      var btnTerm = document.getElementById('nav-btn-terminal');

      if (viewName === 'terminal') {
        if (dashView) dashView.style.display = 'none';
        if (termView) {
          termView.style.display = 'flex';
          termView.style.visibility = 'visible';
        }
        if (btnDash) btnDash.classList.remove('active');
        if (btnTerm) btnTerm.classList.add('active');
        try {
          history.replaceState(null, null, '#terminal');
        } catch (e) {
          window.location.hash = 'terminal';
        }
        [30, 80, 200, 450, 1000].forEach(function(delay) {
          setTimeout(function() {
            window.dispatchEvent(new Event('resize'));
            var chartElem = document.getElementById('chart');
            if (chartElem && typeof window.chart !== 'undefined' && window.chart && window.chart.resize) {
              var nw = chartElem.clientWidth || (window.innerWidth - 380);
              var nh = chartElem.clientHeight || (window.innerHeight - 124);
              if (nw > 50 && nh > 50) {
                window.chart.resize(nw, nh);
                if (window.chart.timeScale) window.chart.timeScale().fitContent();
              }
            }
            if (typeof window.syncCanvasSize === 'function') window.syncCanvasSize();
            if (typeof window.redrawDrawings === 'function') window.redrawDrawings();
          }, delay);
        });
      } else {
        if (dashView) dashView.style.display = 'block';
        if (termView) termView.style.display = 'none';
        if (btnDash) btnDash.classList.add('active');
        if (btnTerm) btnTerm.classList.remove('active');
        try {
          history.replaceState(null, null, window.location.pathname + window.location.search);
        } catch (e) {
          window.location.hash = '';
        }
      }
    }
    window.switchView = switchView;

    function checkUrlForTerminal() {
      var hash = (window.location.hash || '').toLowerCase();
      var path = (window.location.pathname || '').toLowerCase();
      var search = (window.location.search || '').toLowerCase();
      if (hash === '#terminal' || hash.indexOf('terminal') !== -1 || search.indexOf('terminal') !== -1 || path.indexOf('deep') !== -1) {
        switchView('terminal');
      }
    }
    window.addEventListener('hashchange', checkUrlForTerminal);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', checkUrlForTerminal);
    } else {
      checkUrlForTerminal();
    }'''

    assert target_early in content, "target_early switchView not found"

    replacement_early = '''    // ==========================================
    // INSTANT GLOBAL VIEW SWITCHER & ROUTER (EARLY LOAD)
    // ==========================================
    function isUserLoggedIn() {
      if (typeof currentAuthUser !== 'undefined' && currentAuthUser) return true;
      try {
        for (var i = 0; i < localStorage.length; i++) {
          var k = localStorage.key(i);
          if (k && k.indexOf('sb-') !== -1 && k.indexOf('-auth-token') !== -1) {
            var item = localStorage.getItem(k);
            if (item && item.indexOf('"access_token"') !== -1) {
              return true;
            }
          }
        }
      } catch (e) {}
      return false;
    }
    window.isUserLoggedIn = isUserLoggedIn;

    function switchView(viewName) {
      var loggedIn = isUserLoggedIn();
      // If user has logged in, FORBID showing the landing page (view-dashboard) - always keep in terminal/dashboard!
      if (loggedIn) {
        viewName = 'terminal';
      }

      var dashView = document.getElementById('view-dashboard');
      var termView = document.getElementById('view-terminal');
      var btnDash = document.getElementById('nav-btn-dashboard');
      var btnTerm = document.getElementById('nav-btn-terminal');

      if (viewName === 'terminal') {
        if (dashView) dashView.style.display = 'none';
        if (termView) {
          termView.style.display = 'flex';
          termView.style.visibility = 'visible';
        }
        if (btnDash) {
          btnDash.classList.remove('active');
          if (loggedIn) {
            btnDash.style.display = 'none'; // Logged in user stays on their trading dashboard
          }
        }
        if (btnTerm) btnTerm.classList.add('active');
        try {
          history.replaceState(null, null, '#terminal');
        } catch (e) {
          window.location.hash = 'terminal';
        }
        [30, 80, 200, 450, 1000].forEach(function(delay) {
          setTimeout(function() {
            window.dispatchEvent(new Event('resize'));
            var chartElem = document.getElementById('chart');
            if (chartElem && typeof window.chart !== 'undefined' && window.chart && window.chart.resize) {
              var nw = chartElem.clientWidth || (window.innerWidth - 380);
              var nh = chartElem.clientHeight || (window.innerHeight - 124);
              if (nw > 50 && nh > 50) {
                window.chart.resize(nw, nh);
                if (window.chart.timeScale) window.chart.timeScale().fitContent();
              }
            }
            if (typeof window.syncCanvasSize === 'function') window.syncCanvasSize();
            if (typeof window.redrawDrawings === 'function') window.redrawDrawings();
          }, delay);
        });
      } else {
        // Show landing page only when logged out
        if (dashView) dashView.style.display = 'block';
        if (termView) termView.style.display = 'none';
        if (btnDash) {
          btnDash.style.display = '';
          btnDash.classList.add('active');
        }
        if (btnTerm) btnTerm.classList.remove('active');
        try {
          history.replaceState(null, null, window.location.pathname + window.location.search);
        } catch (e) {
          window.location.hash = '';
        }
      }
    }
    window.switchView = switchView;

    function checkUrlForTerminal() {
      var hash = (window.location.hash || '').toLowerCase();
      var path = (window.location.pathname || '').toLowerCase();
      var search = (window.location.search || '').toLowerCase();
      if (isUserLoggedIn() || hash === '#terminal' || hash.indexOf('terminal') !== -1 || search.indexOf('terminal') !== -1 || path.indexOf('deep') !== -1) {
        switchView('terminal');
      } else {
        switchView('dashboard');
      }
    }
    window.addEventListener('hashchange', checkUrlForTerminal);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', checkUrlForTerminal);
    } else {
      checkUrlForTerminal();
    }'''

    content = content.replace(target_early, replacement_early, 1)

    # 2. Update Second switchView and highlightCurrentNav
    target_second = '''    // ==========================================
    // VIEW SWITCHER (Dashboard vs Terminal)
    // ==========================================
        function switchView(viewName) {
      const dashView = document.getElementById('view-dashboard');
      const termView = document.getElementById('view-terminal');
      const btnDash = document.getElementById('nav-btn-dashboard');
      const btnTerm = document.getElementById('nav-btn-terminal');

      if (viewName === 'terminal') {
        if (dashView && termView) {
          dashView.style.display = 'none';
          termView.style.display = 'flex';
          if (btnDash) btnDash.classList.remove('active');
          if (btnTerm) btnTerm.classList.add('active');
          
          try {
            history.replaceState(null, null, '#terminal');
          } catch (e) {
            window.location.hash = 'terminal';
          }

          // Force multiple resize & layout recalculation ticks so LightweightCharts renders immediately
          [30, 80, 200, 450].forEach(delay => {
            setTimeout(() => {
              window.dispatchEvent(new Event('resize'));
              const chartElem = document.getElementById('chart');
              if (chartElem && typeof chart !== 'undefined' && chart.resize) {
                const nw = chartElem.clientWidth || (window.innerWidth - 380);
                const nh = chartElem.clientHeight || (window.innerHeight - 124);
                if (nw > 50 && nh > 50) {
                  chart.resize(nw, nh);
                  if (chart.timeScale) chart.timeScale().fitContent();
                }
              }
              if (typeof syncCanvasSize === 'function') syncCanvasSize();
              if (typeof redrawDrawings === 'function') redrawDrawings();
            }, delay);
          });
          return;
        }
      } else {
        if (dashView && termView) {
          dashView.style.display = 'block';
          termView.style.display = 'none';
          if (btnDash) btnDash.classList.add('active');
          if (btnTerm) btnTerm.classList.remove('active');
          try {
            history.replaceState(null, null, ' ');
          } catch (e) {
            window.location.hash = '';
          }
          return;
        }
      }
    }

    function highlightCurrentNav() {
      const hash = (window.location.hash || '').toLowerCase();
      const path = (window.location.pathname || '').toLowerCase();
      const search = (window.location.search || '').toLowerCase();
      const isTerminal = hash === '#terminal' || 
                         hash.includes('terminal') ||
                         search.includes('terminal') ||
                         path.includes('deep-analysis-gold') ||
                         path.includes('deep_analysis_gold');
      if (isTerminal) {
        switchView('terminal');
      }
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', highlightCurrentNav);
    } else {
      highlightCurrentNav();
    }'''

    assert target_second in content, "target_second switchView not found"

    replacement_second = '''    // ==========================================
    // VIEW SWITCHER (Dashboard vs Terminal)
    // ==========================================
    function switchView(viewName) {
      const loggedIn = (typeof isUserLoggedIn === 'function') ? isUserLoggedIn() : false;
      if (loggedIn) {
        viewName = 'terminal';
      }

      const dashView = document.getElementById('view-dashboard');
      const termView = document.getElementById('view-terminal');
      const btnDash = document.getElementById('nav-btn-dashboard');
      const btnTerm = document.getElementById('nav-btn-terminal');

      if (viewName === 'terminal') {
        if (dashView && termView) {
          dashView.style.display = 'none';
          termView.style.display = 'flex';
          if (btnDash) {
            btnDash.classList.remove('active');
            if (loggedIn) btnDash.style.display = 'none';
          }
          if (btnTerm) btnTerm.classList.add('active');
          
          try {
            history.replaceState(null, null, '#terminal');
          } catch (e) {
            window.location.hash = 'terminal';
          }

          [30, 80, 200, 450].forEach(delay => {
            setTimeout(() => {
              window.dispatchEvent(new Event('resize'));
              const chartElem = document.getElementById('chart');
              if (chartElem && typeof chart !== 'undefined' && chart.resize) {
                const nw = chartElem.clientWidth || (window.innerWidth - 380);
                const nh = chartElem.clientHeight || (window.innerHeight - 124);
                if (nw > 50 && nh > 50) {
                  chart.resize(nw, nh);
                  if (chart.timeScale) chart.timeScale().fitContent();
                }
              }
              if (typeof syncCanvasSize === 'function') syncCanvasSize();
              if (typeof redrawDrawings === 'function') redrawDrawings();
            }, delay);
          });
          return;
        }
      } else {
        if (dashView && termView) {
          dashView.style.display = 'block';
          termView.style.display = 'none';
          if (btnDash) {
            btnDash.style.display = '';
            btnDash.classList.add('active');
          }
          if (btnTerm) btnTerm.classList.remove('active');
          try {
            history.replaceState(null, null, ' ');
          } catch (e) {
            window.location.hash = '';
          }
          return;
        }
      }
    }

    function highlightCurrentNav() {
      const hash = (window.location.hash || '').toLowerCase();
      const path = (window.location.pathname || '').toLowerCase();
      const search = (window.location.search || '').toLowerCase();
      const loggedIn = (typeof isUserLoggedIn === 'function') ? isUserLoggedIn() : false;
      const isTerminal = loggedIn ||
                         hash === '#terminal' || 
                         hash.includes('terminal') ||
                         search.includes('terminal') ||
                         path.includes('deep-analysis-gold') ||
                         path.includes('deep_analysis_gold');
      if (isTerminal) {
        switchView('terminal');
      } else {
        switchView('dashboard');
      }
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', highlightCurrentNav);
    } else {
      highlightCurrentNav();
    }'''

    content = content.replace(target_second, replacement_second, 1)

    # 3. In onUserAuthenticated(user): Immediately switchView('terminal')
    target_on_auth = '''    async function onUserAuthenticated(user) {
      currentAuthUser = user;
      console.log('%c[SUPABASE] User Authenticated:', 'color: #3fb950; font-weight: bold;', user.email);'''

    assert target_on_auth in content, "target_on_auth not found"
    replacement_on_auth = '''    async function onUserAuthenticated(user) {
      currentAuthUser = user;
      console.log('%c[SUPABASE] User Authenticated:', 'color: #3fb950; font-weight: bold;', user.email);
      // Immediately switch to the user's trading terminal/dashboard and hide overview button
      switchView('terminal');
      const navBtnDash = document.getElementById('nav-btn-dashboard');
      if (navBtnDash) navBtnDash.style.display = 'none';'''

    content = content.replace(target_on_auth, replacement_on_auth, 1)

    # 4. In onUserLoggedOut(): switchView('dashboard')
    target_on_logout = '''    function onUserLoggedOut() {
      currentAuthUser = null;
      const navCapsule = document.getElementById('navUserCapsule');'''

    assert target_on_logout in content, "target_on_logout not found"
    replacement_on_logout = '''    function onUserLoggedOut() {
      currentAuthUser = null;
      const navBtnDash = document.getElementById('nav-btn-dashboard');
      if (navBtnDash) navBtnDash.style.display = '';
      // When user logs out, immediately show the overview/landing page
      switchView('dashboard');
      const navCapsule = document.getElementById('navUserCapsule');'''

    content = content.replace(target_on_logout, replacement_on_logout, 1)

    # 5. In handleSupabaseLogout(): clean local storage tokens and show dashboard
    target_handle_logout = '''    async function handleSupabaseLogout() {
      if (supabaseClient) {
        await supabaseClient.auth.signOut();
        currentAuthUser = null;
        onUserLoggedOut();
        if (typeof showSignalToast === 'function') {
          showSignalToast('Logged out of TradingPoint');
        }
      }
    }'''

    assert target_handle_logout in content, "target_handle_logout not found"
    replacement_handle_logout = '''    async function handleSupabaseLogout() {
      if (supabaseClient) {
        try { await supabaseClient.auth.signOut(); } catch (e) {}
      }
      currentAuthUser = null;
      try {
        for (var i = localStorage.length - 1; i >= 0; i--) {
          var k = localStorage.key(i);
          if (k && k.indexOf('sb-') !== -1 && k.indexOf('-auth-token') !== -1) {
            localStorage.removeItem(k);
          }
        }
      } catch (e) {}
      onUserLoggedOut();
      switchView('dashboard');
      if (typeof showSignalToast === 'function') {
        showSignalToast('Logged out of TradingPoint');
      }
    }'''

    content = content.replace(target_handle_logout, replacement_handle_logout, 1)

    # 6. In submitAuthForm(): on login success, switchView('terminal')
    target_submit_auth = '''        if (authMode === 'login') {
          const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
          if (error) throw error;
          showAuthAlert('Login successful! Syncing cloud wallet...', 'success');
          setTimeout(() => { closeAuthModal(); }, 600);
        }'''

    assert target_submit_auth in content, "target_submit_auth not found"
    replacement_submit_auth = '''        if (authMode === 'login') {
          const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
          if (error) throw error;
          showAuthAlert('Login successful! Loading your dashboard...', 'success');
          if (data && data.user) {
            await onUserAuthenticated(data.user);
          }
          switchView('terminal');
          setTimeout(() => { closeAuthModal(); }, 350);
        }'''

    content = content.replace(target_submit_auth, replacement_submit_auth, 1)

    # 7. CSS: Remove hover transform from .btn-primary-cta:hover
    target_cta_hover = '''.btn-primary-cta:hover {
      box-shadow: 0 6px 28px rgba(255, 215, 0, 0.45);
      transform: translateY(-2px);
      color: #000;
    }'''
    assert target_cta_hover in content, "target_cta_hover not found"
    content = content.replace(target_cta_hover, '''.btn-primary-cta:hover {
      box-shadow: 0 6px 28px rgba(255, 215, 0, 0.45);
      transform: none !important;
      color: #000;
    }''', 1)

    # 8. CSS: Remove hover transform from .btn-user-profile-icon:hover
    target_profile_hover = '''.btn-user-profile-icon:hover {
      background: #21262d;
      border-color: #ffd700;
      transform: scale(1.05);
      box-shadow: 0 0 14px rgba(255, 215, 0, 0.45);
    }'''
    assert target_profile_hover in content, "target_profile_hover not found"
    content = content.replace(target_profile_hover, '''.btn-user-profile-icon:hover {
      background: #21262d;
      border-color: #ffd700;
      transform: none !important;
      box-shadow: 0 0 14px rgba(255, 215, 0, 0.45);
    }''', 1)

    # 9. CSS: Remove active transform from .btn-demo-trade:active
    target_trade_active = '''.btn-demo-trade:active {
      transform: scale(0.97);
    }'''
    assert target_trade_active in content, "target_trade_active not found"
    content = content.replace(target_trade_active, '''.btn-demo-trade:active {
      transform: none !important;
      filter: brightness(0.95);
    }''', 1)

    # 10. CSS: Remove pulsing animation on .blinking-dot
    target_blinking = '''.blinking-dot {
      animation: pulse-red-glow 1.5s infinite;
    }'''
    assert target_blinking in content, "target_blinking not found"
    content = content.replace(target_blinking, '''.blinking-dot {
      animation: none !important;
    }''', 1)

    # 11. CSS: Add Universal Zero-Animation, Zero-Lag, Instant Response Rule right before </style>
    target_style_end = '    #chart {'
    assert target_style_end in content, "target_style_end not found"
    zero_lag_css = '''    /* ==========================================
       INSTANT INTERACTION: ZERO SCROLL, MOUSE & CLICK ANIMATION DELAYS
       ========================================== */
    html, body {
      scroll-behavior: auto !important;
    }
    button, a, input, select,
    .view-btn,
    .btn-primary-cta,
    .btn-secondary-cta,
    .btn-demo-trade,
    .btn-user-profile-icon,
    .profile-menu-item,
    .tv-modal,
    .tv-dropdown-menu,
    .profile-dropdown-menu,
    .faq-answer-wrap,
    .blinking-dot,
    .terminal-card,
    .clean-metric-box {
      animation: none !important;
      transition: none !important;
    }
    .btn-primary-cta:hover,
    .btn-secondary-cta:hover,
    .btn-user-profile-icon:hover,
    .profile-menu-item:hover,
    .view-btn:hover,
    .btn-demo-trade:active,
    .clean-metric-box:hover {
      transform: none !important;
    }

    '''
    content = content.replace(target_style_end, zero_lag_css + target_style_end, 1)

    print("All transformations applied successfully.")

    # Write to all 3 files
    for fn in ['gold_dashboard.html', 'deep_analysis_gold.html', 'index.html']:
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Wrote {fn}")

    # Verify MD5 parity
    hashes = {}
    for fn in ['gold_dashboard.html', 'deep_analysis_gold.html', 'index.html']:
        with open(fn, 'rb') as f:
            hashes[fn] = hashlib.md5(f.read()).hexdigest()
        print(f"{fn}: {hashes[fn]}")

    assert len(set(hashes.values())) == 1, "MD5 hashes do not match!"
    print("100% Hash Parity Verified!")

if __name__ == '__main__':
    main()
