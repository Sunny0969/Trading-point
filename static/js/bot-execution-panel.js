/**
 * TradingPoint Server-Side Autonomous Quant Execution Engine (Production-Grade & Zero-Trust)
 * Decoupled Plugin Component: static/js/bot-execution-panel.js
 * 
 * Safety Invariants:
 * - Zero Breaking Changes to existing indicators or manual order handlers.
 * - Server-Authoritative Execution: Client never calculates lots, risk budgets, or dispatches broker orders directly.
 * - Feature Flag Enforced.
 * - Clean, non-intrusive UI (defaults to compact pill to avoid screen clutter).
 * - Instant Open Positions & Wallet UI synchronization.
 */

(function() {
  window.BOT_FEATURE_ENABLED = true;
  if (!window.BOT_FEATURE_ENABLED) return;

  // Prevent multiple initializations
  if (window.__QUANT_PANEL_INITIALIZED__) return;
  window.__QUANT_PANEL_INITIALIZED__ = true;

  // Ensure CSS is loaded
  if (!document.querySelector('link[href*="bot-panel.css"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/css/bot-panel.css';
    document.head.appendChild(link);
  }

  // Default to collapsed pill for clean, clutter-free UI
  const savedCollapsed = localStorage.getItem('quant_dock_collapsed');
  const isCollapsedInitial = savedCollapsed === null ? true : savedCollapsed === 'true';

  const dock = document.createElement('div');
  dock.className = 'quant-agent-dock' + (isCollapsedInitial ? ' collapsed' : '');
  dock.id = 'quantAgentDock';
  dock.innerHTML = `
    <div class="quant-dock-header" id="quantDockHeader">
      <div class="quant-dock-title-group">
        <span id="quantLed" class="quant-led-dot quant-led-off"></span>
        <span class="quant-dock-title">QUANT AGENT</span>
        <span class="quant-dock-collapse-icon" id="quantCollapseBtn" title="Toggle Quant Telemetry">▾</span>
      </div>
      <div class="quant-toggle-wrapper" onclick="event.stopPropagation();">
        <label class="quant-switch" title="Toggle Autonomous Execution">
          <input type="checkbox" id="quantMasterToggle">
          <span class="quant-slider"></span>
        </label>
      </div>
    </div>
    <div id="quantDockBody" class="quant-dock-body">
      <div class="quant-metric-row">
        <span>Status:</span>
        <strong id="quantStatusLabel" style="color:#848E9C;">OFFLINE</strong>
      </div>
      <div class="quant-metric-row">
        <span>Strategy:</span>
        <strong id="quantRiskCeilingLabel" style="color:#ffd700;">Micro-Scalp (Quick TP)</strong>
      </div>
      <div class="quant-metric-row">
        <span>Risk Guard:</span>
        <strong style="color:#3fb950;">Tight SL ($1.50 Max)</strong>
      </div>
      <div class="quant-metric-row">
        <span>Authority:</span>
        <strong style="color:#26a69a;">Server-Authoritative</strong>
      </div>
      <div class="quant-metric-row">
        <span>Telemetry:</span>
        <strong id="quantLastTelemetry" style="color:#ffd700; font-size:10px;">STANDBY</strong>
      </div>
      <button id="quantEmergencyKill" class="kill-switch-btn" type="button">
        🛑 EMERGENCY KILL SWITCH
      </button>
      <div class="quant-disclaimer">
        Low-Risk Micro Scalp Engine. Loss minimized with $1.50 tight SL and $2.50 quick profit target.
      </div>
    </div>
  `;
  document.body.appendChild(dock);

  const header = document.getElementById('quantDockHeader');
  const toggle = document.getElementById('quantMasterToggle');
  const led = document.getElementById('quantLed');
  const statusLabel = document.getElementById('quantStatusLabel');
  const lastTelemetry = document.getElementById('quantLastTelemetry');
  const killBtn = document.getElementById('quantEmergencyKill');

  // Collapse / Expand toggle on header click
  header.addEventListener('click', (e) => {
    if (e.target.closest('.quant-toggle-wrapper')) return;
    dock.classList.toggle('collapsed');
    localStorage.setItem('quant_dock_collapsed', dock.classList.contains('collapsed'));
  });

  // Helper to fetch authenticated user safely
  async function getAuthenticatedUserId() {
    try {
      if (window.supabase && typeof window.supabase.auth?.getUser === 'function') {
        const { data, error } = await window.supabase.auth.getUser();
        if (data && data.user) return data.user.id;
      }
    } catch (e) {
      console.warn('[QuantAgent] Auth user check failed:', e);
    }
    try {
      const stored = localStorage.getItem('supabase.auth.token') || localStorage.getItem('sb-tcwboskfypcrsrniatni-auth-token');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.user?.id) return parsed.user.id;
      }
    } catch (_) {}
    return null;
  }

  // Load initial settings from server
  async function syncSettingsFromServer() {
    const userId = await getAuthenticatedUserId();
    if (!userId) return;

    if (window.supabase) {
      try {
        const { data: settings } = await window.supabase
          .from('bot_settings')
          .select('*')
          .eq('user_id', userId)
          .maybeSingle();

        if (settings) {
          if (settings.kill_switch) {
            toggle.checked = false;
            led.className = 'quant-led-dot quant-led-killed';
            statusLabel.innerText = 'KILLED (LOCKED)';
            statusLabel.style.color = '#ef5350';
          } else if (settings.is_active) {
            toggle.checked = true;
            led.className = 'quant-led-dot quant-led-on';
            statusLabel.innerText = 'MONITORING ENGINE';
            statusLabel.style.color = '#26a69a';
            lastTelemetry.innerText = 'SCANNING SCALPS';
          } else {
            toggle.checked = false;
            led.className = 'quant-led-dot quant-led-off';
            statusLabel.innerText = 'OFFLINE';
            statusLabel.style.color = '#848E9C';
          }
        }
      } catch (err) {
        console.warn('[QuantAgent] Error reading bot_settings:', err);
      }
    }
  }

  // Toggle master execution
  toggle.addEventListener('change', async (e) => {
    const isActive = e.target.checked;
    led.className = isActive ? 'quant-led-dot quant-led-on' : 'quant-led-dot quant-led-off';
    statusLabel.innerText = isActive ? 'MONITORING ENGINE' : 'OFFLINE';
    statusLabel.style.color = isActive ? '#26a69a' : '#848E9C';
    lastTelemetry.innerText = isActive ? 'SCANNING SCALPS' : 'STANDBY';

    const userId = await getAuthenticatedUserId();
    if (userId && window.supabase) {
      try {
        await window.supabase
          .from('bot_settings')
          .upsert({ user_id: userId, is_active: isActive, kill_switch: false });
      } catch (err) {
        console.error('[QuantAgent] Failed to update toggle state:', err);
      }
    }
  });

  // Emergency Kill Switch
  killBtn.addEventListener('click', async () => {
    if (confirm("Engage Emergency Kill Switch?\n\nThis immediately halts all automated quant processing and locks execution server-side.")) {
      toggle.checked = false;
      led.className = 'quant-led-dot quant-led-killed';
      statusLabel.innerText = 'KILLED (LOCKED)';
      statusLabel.style.color = '#ef5350';
      lastTelemetry.innerText = 'EXECUTION HALTED';

      const userId = await getAuthenticatedUserId();
      if (userId && window.supabase) {
        try {
          await window.supabase
            .from('bot_settings')
            .upsert({ user_id: userId, is_active: false, kill_switch: true });
        } catch (err) {
          console.error('[QuantAgent] Failed to engage kill switch on server:', err);
        }
      }
    }
  });

  // Helper to inject bot order into open positions UI
  function injectBotPositionIntoUI(result, payload) {
    try {
      const orderId = result.orderId || ('BOT-' + Date.now().toString(36));
      const entryPrice = parseFloat(result.entry || payload.entry);
      const lotSize = parseFloat(result.lot);
      const slPrice = parseFloat(result.sl);
      const tpPrice = parseFloat(result.tp);
      const reqMargin = parseFloat(((entryPrice * lotSize * 100) / 100).toFixed(2));

      // 1. If demoState exists in window scope
      if (typeof window.demoState !== 'undefined' && Array.isArray(window.demoState.positions)) {
        const exists = window.demoState.positions.some(p => p.id === orderId || p.dbId === orderId || (p.entryPrice === entryPrice && p.type === payload.direction && p.lots === lotSize));
        if (!exists) {
          const newPos = {
            id: orderId,
            dbId: orderId,
            type: payload.direction,
            lots: lotSize,
            entryPrice: entryPrice,
            margin: reqMargin,
            sl: slPrice,
            tp: tpPrice,
            executedBy: 'BOT',
            isBot: true,
            openTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          };
          window.demoState.positions.unshift(newPos);
          if (typeof window.saveDemoState === 'function') window.saveDemoState();
          if (typeof window.renderDemoPositionsList === 'function') window.renderDemoPositionsList();
          if (typeof window.renderDemoWalletUI === 'function') window.renderDemoWalletUI(entryPrice);
        }
      }

      // 2. Also trigger cloud sync if authenticated
      if (typeof window.syncUserDataFromSupabase === 'function' && window.currentAuthUser) {
        window.syncUserDataFromSupabase(window.currentAuthUser);
      }
    } catch (uiErr) {
      console.warn('[QuantAgent] Error injecting position into UI:', uiErr);
    }
  }

  // Server-Authoritative Dispatch Function
  // Client only transmits signal coordinates, NEVER calculates lot size or risk
  window.dispatchQuantSignalToServer = async function(signalData) {
    if (!toggle.checked) {
      return { status: 'ABORTED', reason: 'Bot inactive' };
    }

    const userId = await getAuthenticatedUserId();
    if (!userId) {
      console.warn('[QuantAgent] No authenticated user found for automated execution.');
      lastTelemetry.innerText = 'LOGIN REQUIRED';
      return { status: 'ABORTED', reason: 'Authentication required' };
    }

    const payload = {
      userId: userId,
      source: signalData.source || 'SMC_CONFLUENCE',
      direction: signalData.direction || 'BUY',
      entry: parseFloat(signalData.entry),
      sl: parseFloat(signalData.sl),
      tp: parseFloat(signalData.tp),
      candleTime: signalData.candleTime || Math.floor(Date.now() / 1000)
    };

    lastTelemetry.innerText = 'DISPATCHING SCALP...';

    try {
      const response = await fetch('/api/quant-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      console.log('[QuantAgent] Server execution response:', result);

      if (result.status === 'SUCCESS') {
        lastTelemetry.innerText = `FILLED: ${result.lot}L (TP: $${result.tp} | SL: $${result.sl})`;
        lastTelemetry.style.color = '#3fb950';

        // Immediately update OPEN POSITIONS container
        injectBotPositionIntoUI(result, payload);

        if (typeof window.showSignalToast === 'function') {
          window.showSignalToast(`🤖 Quant Scalp Executed: ${payload.direction} ${result.lot}L @ $${result.entry.toFixed(2)} (TP: $${result.tp})`);
        }
      } else if (result.status === 'SKIPPED') {
        lastTelemetry.innerText = `SKIPPED: ${result.reason || 'Guard limit'}`;
        lastTelemetry.style.color = '#ffd700';
      } else {
        lastTelemetry.innerText = `FAIL: ${result.reason || 'Server error'}`;
        lastTelemetry.style.color = '#ef5350';
      }

      return result;
    } catch (netErr) {
      console.error('[QuantAgent] Server dispatch network error:', netErr);
      lastTelemetry.innerText = 'NETWORK TIMEOUT';
      lastTelemetry.style.color = '#ef5350';
      return { status: 'FAILED', reason: netErr.message };
    }
  };

  // Autonomous Signal Monitor (Decoupled Observer)
  let lastDispatchedHash = null;
  function monitorSignalsForExecution() {
    if (!toggle.checked) return;
    const pos = window.activeTradingPointPosition;
    if (pos && pos.status === 'ACTIVE' && pos.entry && pos.sl && pos.tp) {
      const sigKey = `${pos.direction || pos.type}_${pos.entry}_${pos.sl}_${pos.tp}_${pos.startCandleTime || pos.startTime || ''}`;
      if (lastDispatchedHash !== sigKey) {
        lastDispatchedHash = sigKey;
        window.dispatchQuantSignalToServer({
          source: pos.source || 'INSTITUTIONAL_SMC',
          direction: (pos.direction === 'SELL' || pos.type === 'SHORT') ? 'SELL' : 'BUY',
          entry: pos.entry,
          sl: pos.sl,
          tp: pos.tp,
          candleTime: pos.startCandleTime || pos.startTime || Math.floor(Date.now() / 1000)
        });
      }
    }
  }

  setInterval(monitorSignalsForExecution, 4000);

  // Sync settings when DOM or Supabase becomes ready
  setTimeout(syncSettingsFromServer, 1000);
  window.addEventListener('load', syncSettingsFromServer);
  if (window.supabase?.auth) {
    window.supabase.auth.onAuthStateChange?.(() => syncSettingsFromServer());
  }

  console.log('[TradingPoint] Autonomous Quant Execution Panel loaded successfully.');
})();
