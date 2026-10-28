"""
Apply:
1. Strict 100% Target Synchronization between 3-Candle Ghost Prediction and Execution Signals Card (e.g. $4118.70).
2. Abolish 15-Minute Rigid Lock: Replace with Agile Real-Time Scanner (Live Agile Scanner, Runner Active with Breakeven Trailing).
3. FOMC / Economic News In-Play Detector & Liquidity Sweep V-Shape Reversal Engine.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

def apply_upgrades(filepath):
    print(f"Applying Ghost Sync & Agile Scanner upgrades to {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # =========================================================================
    # 1. SYNCHRONIZE 3-CANDLE GHOST PREDICTION TARGET WITH EXECUTION SIGNALS CARD
    # =========================================================================
    target_ghost_pattern = """      // Candlestick Pattern Trajectory Confluence & Next Candle Prediction
      if (typeof currentCandlePattern !== 'undefined' && currentCandlePattern) {
        if (currentCandlePattern.bias.includes('BULLISH')) {
          const push = currentCandlePattern.netTargetPush || (2.0 * atr);
          c1_open = currentPrice;
          c1_close = c1_open + (atr * 1.8);
          c1_high = Math.max(lastCandle.high + 0.8, c1_close + (atr * 0.35));
          c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close;
          c2_close = c2_open + (atr * 0.75);
          c2_high = c2_close + (atr * 0.35);
          c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close;
          c3_close = Math.max(currentPrice + push, c3_open + (atr * 0.85));
          c3_high = c3_close + (atr * 0.45);
          c3_low = c3_open - (atr * 0.20);
          targetLabel = `🎯 Target $${c3_close.toFixed(1)} (${currentCandlePattern.pattern.split(' ')[1] || 'Expansion'})`;
          targetColor = '#2ea043';
          isUp = true;
        } else if (currentCandlePattern.bias.includes('BEARISH')) {
          const drop = Math.abs(currentCandlePattern.netTargetPush || (2.0 * atr));
          const emaTarget = (typeof ema20Val === 'number' && ema20Val > 0) ? ema20Val : (currentPrice - (2.0 * atr));
          c1_open = currentPrice;
          c1_close = c1_open - (atr * 1.8);
          c1_low = Math.min(emaTarget, c1_close - (atr * 0.35));
          c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close;
          c2_close = Math.min(c2_open - (atr * 0.75), emaTarget);
          c2_low = c2_close - (atr * 0.35);
          c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close;
          c3_close = Math.min(currentPrice - drop, emaTarget - (0.5 * atr));
          c3_low = c3_close - (atr * 0.45);
          c3_high = c3_open + (atr * 0.20);
          targetLabel = `🎯 Target $${c3_close.toFixed(1)} (${currentCandlePattern.pattern.split(' ')[1] || 'Retracement'})`;
          targetColor = '#f85149';
          isUp = false;
        }
      }"""

    replacement_ghost_pattern = """      // Candlestick Pattern Trajectory Confluence & Next Candle Prediction
      if (typeof currentCandlePattern !== 'undefined' && currentCandlePattern) {
        if (currentCandlePattern.bias.includes('BULLISH')) {
          const push = currentCandlePattern.netTargetPush || (2.0 * atr);
          c1_open = currentPrice;
          c1_close = c1_open + (atr * 1.8);
          c1_high = Math.max(lastCandle.high + 0.8, c1_close + (atr * 0.35));
          c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close;
          c2_close = c2_open + (atr * 0.75);
          c2_high = c2_close + (atr * 0.35);
          c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close;
          c3_close = Math.max(currentPrice + push, c3_open + (atr * 0.85));
          c3_high = c3_close + (atr * 0.45);
          c3_low = c3_open - (atr * 0.20);
          targetLabel = `🎯 Target $${c3_close.toFixed(1)} (${currentCandlePattern.pattern.split(' ')[1] || 'Expansion'})`;
          targetColor = '#2ea043';
          isUp = true;

          // STRICT BIDIRECTIONAL SYNC: Synchronize Execution Signals Card Target to match $c3_close!
          if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) {
            shortTermSignalLock.tp1 = Number(c3_close.toFixed(2));
            shortTermSignalLock.gainPts = Number(Math.abs(c3_close - shortTermSignalLock.entryPrice).toFixed(1));
            const risk = Math.max(2.0, Math.abs(shortTermSignalLock.entryPrice - shortTermSignalLock.sl));
            shortTermSignalLock.rrText = `1 : ${(shortTermSignalLock.gainPts / risk).toFixed(1)} (+${shortTermSignalLock.gainPts.toFixed(1)} pts)`;

            const stTp = document.getElementById('stTpVal');
            const stRr = document.getElementById('stRrVal');
            if (stTp) stTp.innerText = '$' + shortTermSignalLock.tp1.toFixed(2);
            if (stRr) stRr.innerText = shortTermSignalLock.rrText;
          }
        } else if (currentCandlePattern.bias.includes('BEARISH')) {
          const drop = Math.abs(currentCandlePattern.netTargetPush || (2.0 * atr));
          const emaTarget = (typeof ema20Val === 'number' && ema20Val > 0) ? ema20Val : (currentPrice - (2.0 * atr));
          c1_open = currentPrice;
          c1_close = c1_open - (atr * 1.8);
          c1_low = Math.min(emaTarget, c1_close - (atr * 0.35));
          c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close;
          c2_close = Math.min(c2_open - (atr * 0.75), emaTarget);
          c2_low = c2_close - (atr * 0.35);
          c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close;
          c3_close = Math.min(currentPrice - drop, emaTarget - (0.5 * atr));
          c3_low = c3_close - (atr * 0.45);
          c3_high = c3_open + (atr * 0.20);
          targetLabel = `🎯 Target $${c3_close.toFixed(1)} (${currentCandlePattern.pattern.split(' ')[1] || 'Retracement'})`;
          targetColor = '#f85149';
          isUp = false;

          // STRICT BIDIRECTIONAL SYNC: Synchronize Execution Signals Card Target to match $c3_close!
          if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) {
            shortTermSignalLock.tp1 = Number(c3_close.toFixed(2));
            shortTermSignalLock.gainPts = Number(Math.abs(shortTermSignalLock.entryPrice - c3_close).toFixed(1));
            const risk = Math.max(2.0, Math.abs(shortTermSignalLock.sl - shortTermSignalLock.entryPrice));
            shortTermSignalLock.rrText = `1 : ${(shortTermSignalLock.gainPts / risk).toFixed(1)} (+${shortTermSignalLock.gainPts.toFixed(1)} pts)`;

            const stTp = document.getElementById('stTpVal');
            const stRr = document.getElementById('stRrVal');
            if (stTp) stTp.innerText = '$' + shortTermSignalLock.tp1.toFixed(2);
            if (stRr) stRr.innerText = shortTermSignalLock.rrText;
          }
        }
      }"""

    if target_ghost_pattern in content:
        content = content.replace(target_ghost_pattern, replacement_ghost_pattern)
        print(" [x] Enforced Strict Bidirectional Target Sync between Ghost Prediction and Signal Card.")
    else:
        print(" [!] Could not find target_ghost_pattern.")

    # When shortTermSignalLock.active is running, Ghost candle c3_close must target shortTermSignalLock.tp1
    target_active_ghost = """      } else if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock.active) {
        isUp = (shortTermSignalLock.signalType === 'BUY');
        const tp1 = shortTermSignalLock.tp1;
        targetLabel = isUp 
          ? `🎯 Target $${tp1.toFixed(1)} (15M Scalp)`
          : `🎯 Target $${tp1.toFixed(1)} (15M Scalp)`;
        targetColor = isUp ? '#2ea043' : '#f85149';

        if (isUp) {
          c1_open = currentPrice; c1_close = c1_open + (atr * 0.60); c1_high = c1_close + (atr * 0.35); c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open + (atr * 0.75); c2_high = c2_close + (atr * 0.40); c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close; c3_close = Math.max(tp1, c3_open + (atr * 0.85)); c3_high = c3_close + (atr * 0.45); c3_low = c3_open - (atr * 0.20);
        } else {
          c1_open = currentPrice; c1_close = c1_open - (atr * 0.60); c1_low = c1_close - (atr * 0.35); c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open - (atr * 0.75); c2_low = c2_close - (atr * 0.40); c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close; c3_close = Math.min(tp1, c3_open - (atr * 0.85)); c3_low = c3_close - (atr * 0.45); c3_high = c3_open + (atr * 0.20);
        }
      }"""

    replacement_active_ghost = """      } else if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock.active) {
        isUp = (shortTermSignalLock.signalType === 'BUY');
        const tp1 = Number(shortTermSignalLock.tp1);
        targetLabel = `🎯 Target $${tp1.toFixed(1)} (${isUp ? 'Bullish' : 'Bearish'})`;
        targetColor = isUp ? '#2ea043' : '#f85149';

        if (isUp) {
          c1_open = currentPrice; c1_close = c1_open + (atr * 0.60); c1_high = c1_close + (atr * 0.35); c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open + (atr * 0.75); c2_high = c2_close + (atr * 0.40); c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close; c3_close = tp1; c3_high = c3_close + (atr * 0.45); c3_low = c3_open - (atr * 0.20);
        } else {
          c1_open = currentPrice; c1_close = c1_open - (atr * 0.60); c1_low = c1_close - (atr * 0.35); c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open - (atr * 0.75); c2_low = c2_close - (atr * 0.40); c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close; c3_close = tp1; c3_low = c3_close - (atr * 0.45); c3_high = c3_open + (atr * 0.20);
        }
      }"""

    if target_active_ghost in content:
        content = content.replace(target_active_ghost, replacement_active_ghost)
        print(" [x] Bound Ghost 3rd Candle c3_close precisely to shortTermSignalLock.tp1.")
    else:
        print(" [!] Could not find target_active_ghost.")

    # =========================================================================
    # 2. ABOLISH 15-MINUTE RIGID LOCK & INTRODUCE AGILE EXPANSION RUNNER ENGINE
    # =========================================================================
    target_lock_init = """    var shortTermSignalLock = {
      active: false,
      action: 'BUY / LONG',
      signalType: 'BUY',
      confidence: '5/5 Timeframes Aligned (4H Macro + 15M Shift + 5M OB + 3M Entry)',
      entryZoneText: '$4,008.50 - $4,010.50',
      entryPrice: 4009.50,
      tp1: 4025.50,
      tp2: 4033.50,
      sl: 4001.50,
      rrText: '1 : 3.0 (+16.0 pts)',
      gainPts: 16.0,
      reason: '4H Bullish Trend + 15M Shift + 5M OB Retest + 3M Wick Absorption.',
      lockedAt: Date.now(),
      minLockDurationMs: 15 * 60 * 1000,
      maxLockDurationMs: 60 * 60 * 1000,
      status: 'ACTIVE_HOLD',         // 'ACTIVE_HOLD', 'TP_HIT', 'SL_HIT'
      completedAt: null,
      lastCompletedType: null,
      lastCompletedStatus: null
    };"""

    replacement_lock_init = """    var shortTermSignalLock = {
      active: false,
      action: 'BUY / LONG',
      signalType: 'BUY',
      confidence: '5/5 Timeframes Aligned (Agile Real-Time Execution)',
      entryZoneText: '$4,069.00 - $4,071.00',
      entryPrice: 4069.96,
      tp1: 4118.70,
      tp2: 4128.50,
      sl: 4066.96,
      rrText: '1 : 3.2 (+48.7 pts)',
      gainPts: 48.7,
      reason: 'FOMC Liquidity Sweep Complete @ Demand Floor ($4042.69) -> V-Shape Reversal Expansion.',
      lockedAt: Date.now(),
      minLockDurationMs: 0,           // AGILE: NO RIGID 15-MIN FREEZE!
      maxLockDurationMs: 60 * 60 * 1000,
      status: 'ACTIVE_HOLD',         // 'ACTIVE_HOLD', 'RUNNER_ACTIVE', 'TP_HIT', 'SL_HIT'
      completedAt: null,
      lastCompletedType: null,
      lastCompletedStatus: null
    };"""

    if target_lock_init in content:
        content = content.replace(target_lock_init, replacement_lock_init)
        print(" [x] Abolished rigid 15-minute lock in shortTermSignalLock initialization.")
    else:
        print(" [!] Could not find target_lock_init.")

    # Upgrade TP Evaluation in updateActiveSetupCard for Dynamic Expansion Runner
    target_tp_eval = """        } else if (shortTermSignalLock.status === 'ACTIVE_HOLD') {
          if (isBuy && currentSpot >= shortTermSignalLock.tp1) {
            shortTermSignalLock.status = 'TP_HIT';
            shortTermSignalLock.completedAt = now;
            shortTermSignalLock.lastCompletedType = 'BUY';
            shortTermSignalLock.lastCompletedStatus = 'TP_HIT';
          } else if (!isBuy && currentSpot <= shortTermSignalLock.tp1) {
            shortTermSignalLock.status = 'TP_HIT';
            shortTermSignalLock.completedAt = now;
            shortTermSignalLock.lastCompletedType = 'SELL';
            shortTermSignalLock.lastCompletedStatus = 'TP_HIT';
          }
        }"""

    replacement_tp_eval = """        } else if (shortTermSignalLock.status === 'ACTIVE_HOLD' || shortTermSignalLock.status === 'RUNNER_ACTIVE') {
          // Dynamic Expansion Runner Logic: If price surges strongly past initial targets (like in FOMC/News)
          if (isBuy && currentSpot >= shortTermSignalLock.tp1) {
            if (currentSpot >= (shortTermSignalLock.tp1 + 2.0) && shortTermSignalLock.status !== 'RUNNER_ACTIVE') {
              // Convert to ACTIVE RUNNER: Trail Stop to Breakeven & Advance Target to Overhead Liquidity!
              const extendedTarget = Math.max(shortTermSignalLock.tp1 + 15.0, currentSpot + 8.0);
              shortTermSignalLock.status = 'RUNNER_ACTIVE';
              shortTermSignalLock.sl = Number(shortTermSignalLock.entryPrice.toFixed(2)); // TRAIL SL TO BREAKEVEN!
              shortTermSignalLock.tp1 = Number(extendedTarget.toFixed(2));
              shortTermSignalLock.action = 'BULLISH EXPANSION RUNNER';
              shortTermSignalLock.confidence = 'Runner Active (Stop at Breakeven · Risk-Free)';
              shortTermSignalLock.reason = `Initial target achieved! Trailing stop locked at Breakeven ($${shortTermSignalLock.entryPrice.toFixed(2)}). Expanding to $${extendedTarget.toFixed(1)}.`;
            } else {
              shortTermSignalLock.status = 'TP_HIT';
              shortTermSignalLock.completedAt = now;
              shortTermSignalLock.lastCompletedType = 'BUY';
              shortTermSignalLock.lastCompletedStatus = 'TP_HIT';
            }
          } else if (!isBuy && currentSpot <= shortTermSignalLock.tp1) {
            if (currentSpot <= (shortTermSignalLock.tp1 - 2.0) && shortTermSignalLock.status !== 'RUNNER_ACTIVE') {
              const extendedTarget = Math.min(shortTermSignalLock.tp1 - 15.0, currentSpot - 8.0);
              shortTermSignalLock.status = 'RUNNER_ACTIVE';
              shortTermSignalLock.sl = Number(shortTermSignalLock.entryPrice.toFixed(2)); // TRAIL SL TO BREAKEVEN!
              shortTermSignalLock.tp1 = Number(extendedTarget.toFixed(2));
              shortTermSignalLock.action = 'BEARISH EXPANSION RUNNER';
              shortTermSignalLock.confidence = 'Runner Active (Stop at Breakeven · Risk-Free)';
              shortTermSignalLock.reason = `Initial target achieved! Trailing stop locked at Breakeven ($${shortTermSignalLock.entryPrice.toFixed(2)}). Expanding to $${extendedTarget.toFixed(1)}.`;
            } else {
              shortTermSignalLock.status = 'TP_HIT';
              shortTermSignalLock.completedAt = now;
              shortTermSignalLock.lastCompletedType = 'SELL';
              shortTermSignalLock.lastCompletedStatus = 'TP_HIT';
            }
          }
        }"""

    if target_tp_eval in content:
        content = content.replace(target_tp_eval, replacement_tp_eval)
        print(" [x] Upgraded TP evaluation with Dynamic Expansion Runner & Breakeven Trailing.")
    else:
        print(" [!] Could not find target_tp_eval.")

    # Remove rigid lock timer countdown and replace with Agile Real-Time Scanner badge
    target_st_timer_ui = """        } else {
          const curElapsed = now - shortTermSignalLock.lockedAt;
          if (curElapsed < shortTermSignalLock.minLockDurationMs) {
            const remSec = Math.max(0, Math.ceil((shortTermSignalLock.minLockDurationMs - curElapsed) / 1000));
            const mins = Math.floor(remSec / 60);
            const secs = remSec % 60;
            stTimer.innerText = '🔒 LOCKED: ' + mins + 'm ' + (secs < 10 ? '0' : '') + secs + 's';
            stTimer.style.background = 'rgba(46,160,67,0.15)';
            stTimer.style.color = '#3fb950';
            stTimer.style.borderColor = 'rgba(46,160,67,0.3)';
          } else {
            const holdMins = Math.min(60, Math.floor(curElapsed / 60000));
            stTimer.innerText = '⏱️ 1H HOLD: ' + holdMins + 'm / 60m';
            stTimer.style.background = 'rgba(88,166,255,0.15)';
            stTimer.style.color = '#58a6ff';
            stTimer.style.borderColor = 'rgba(88,166,255,0.3)';
          }
        }"""

    replacement_st_timer_ui = """        } else if (shortTermSignalLock.status === 'RUNNER_ACTIVE') {
          stTimer.innerText = '🚀 EXPANSION RUNNER ACTIVE';
          stTimer.style.background = 'rgba(56, 189, 248, 0.2)';
          stTimer.style.color = '#38bdf8';
          stTimer.style.borderColor = 'rgba(56, 189, 248, 0.5)';
        } else {
          // Agile Real-Time Scanner (No rigid 15-minute lock!)
          stTimer.innerText = '⚡ LIVE AGILE SCANNER';
          stTimer.style.background = 'rgba(46, 160, 67, 0.15)';
          stTimer.style.color = '#3fb950';
          stTimer.style.borderColor = 'rgba(46, 160, 67, 0.3)';
        }"""

    if target_st_timer_ui in content:
        content = content.replace(target_st_timer_ui, replacement_st_timer_ui)
        print(" [x] Replaced rigid lock timer UI with Agile Real-Time Scanner badge.")
    else:
        print(" [!] Could not find target_st_timer_ui.")

    # Also update initial HTML badge text
    target_html_badge = """<span id="stLockTimer" class="tag-badge" style="background: rgba(46,160,67,0.15); color: #3fb950; border: 1px solid rgba(46,160,67,0.3); font-size: 10px; font-weight: 700;">🔒 LOCKED: 14m 59s</span>"""
    replacement_html_badge = """<span id="stLockTimer" class="tag-badge" style="background: rgba(46,160,67,0.15); color: #3fb950; border: 1px solid rgba(46,160,67,0.3); font-size: 10px; font-weight: 700;">⚡ LIVE AGILE SCANNER</span>"""
    if target_html_badge in content:
        content = content.replace(target_html_badge, replacement_html_badge)
        print(" [x] Updated initial HTML stLockTimer badge to '⚡ LIVE AGILE SCANNER'.")

    # In updateActiveSetupCard transition reset minLockDurationMs = 0
    content = content.replace("minLockDurationMs: 15 * 60 * 1000,", "minLockDurationMs: 0,")

    # =========================================================================
    # 3. FOMC & HIGH-IMPACT NEWS IN-PLAY DETECTION ENGINE
    # =========================================================================
    target_news_fetch = """          const upcoming = data
            .map(e => ({ ...e, timeMs: new Date(e.date).getTime() }))
            .filter(e => e.timeMs > now)
            .sort((a, b) => a.timeMs - b.timeMs);"""

    replacement_news_fetch = """          // Detect active in-play high-impact events (released within last 120 mins or upcoming in 30 mins)
          const inPlayEvent = data
            .map(e => ({ ...e, timeMs: new Date(e.date).getTime() }))
            .find(e => {
              const diffMin = (now - e.timeMs) / 60000;
              const isMacroKey = e.impact === 'High' || /FOMC|Fed|Interest Rate|CPI|NFP|Powell|Employment/i.test(e.title);
              return isMacroKey && (diffMin >= -30 && diffMin <= 120);
            });

          if (inPlayEvent) {
            window.activeNewsEvent = inPlayEvent;
          }

          const upcoming = data
            .map(e => ({ ...e, timeMs: new Date(e.date).getTime() }))
            .filter(e => e.timeMs > now)
            .sort((a, b) => a.timeMs - b.timeMs);"""

    if target_news_fetch in content:
        content = content.replace(target_news_fetch, replacement_news_fetch)
        print(" [x] Added active in-play high-impact news event detection in fetchMostRecentNews.")
    else:
        print(" [!] Could not find target_news_fetch.")

    # Update inPlayEvent UI in fetchMostRecentNews
    target_news_ui_set = """            if (homeNewsHeadline) homeNewsHeadline.innerText = titleStr;
            if (homeNewsCountdown) homeNewsCountdown.innerText = countdownStr;
            if (homeNewsRiskBadge) { homeNewsRiskBadge.innerText = riskStr; homeNewsRiskBadge.className = riskClass; }
            if (homeNewsImpactDirection) homeNewsImpactDirection.innerText = impactStr;"""

    replacement_news_ui_set = """            if (inPlayEvent) {
              const elapsedMin = Math.round((now - inPlayEvent.timeMs) / 60000);
              const inPlayHeadline = `🔴 ${inPlayEvent.title.toUpperCase()} IN PLAY (${elapsedMin >= 0 ? elapsedMin + 'm AGO' : 'IN ' + Math.abs(elapsedMin) + 'm'})`;
              if (newsHeadline) newsHeadline.innerText = inPlayHeadline;
              if (homeNewsHeadline) homeNewsHeadline.innerText = inPlayHeadline;
              if (newsRiskBadge) { newsRiskBadge.innerText = '🔴 HIGH VOLATILITY LIVE'; newsRiskBadge.className = 'tag-badge tag-bearish'; }
              if (homeNewsRiskBadge) { homeNewsRiskBadge.innerText = '🔴 HIGH VOLATILITY LIVE'; homeNewsRiskBadge.className = 'tag-badge tag-bearish'; }
              if (newsCountdown) newsCountdown.innerText = 'EVENT IN PLAY';
              if (homeNewsCountdown) homeNewsCountdown.innerText = 'EVENT IN PLAY';
            } else {
              if (homeNewsHeadline) homeNewsHeadline.innerText = titleStr;
              if (homeNewsCountdown) homeNewsCountdown.innerText = countdownStr;
              if (homeNewsRiskBadge) { homeNewsRiskBadge.innerText = riskStr; homeNewsRiskBadge.className = riskClass; }
              if (homeNewsImpactDirection) homeNewsImpactDirection.innerText = impactStr;
            }"""

    if target_news_ui_set in content:
        content = content.replace(target_news_ui_set, replacement_news_ui_set)
        print(" [x] Added in-play high-impact news UI banner.")
    else:
        print(" [!] Could not find target_news_ui_set.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {filepath} ({len(content):,} bytes).\n")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        apply_upgrades(fn)
