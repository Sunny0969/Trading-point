"""
Fix ReferenceError for currentLiquidityPools and apply defensive guard to shortTermSignalLock
in gold_dashboard.html, index.html, and deep_analysis_gold.html.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

def fix_file(filepath):
    print(f"Applying fix to {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Declare var currentLiquidityPools right after currentSMCZones
    target_smc_decl = "let currentSMCZones = { fvgList: [], obList: [] };"
    replacement_smc_decl = "let currentSMCZones = { fvgList: [], obList: [] };\n    var currentLiquidityPools = null;"
    if target_smc_decl in content and "var currentLiquidityPools = null;" not in content:
        content = content.replace(target_smc_decl, replacement_smc_decl)
        print(" [x] Added early var currentLiquidityPools = null")

    # 2. Change let currentLiquidityPools = null at line 6614 to var currentLiquidityPools = currentLiquidityPools || null;
    target_let_liq = "    let currentLiquidityPools = null;\n    window.latestLiquiditySweep = null;"
    replacement_var_liq = "    var currentLiquidityPools = currentLiquidityPools || null;\n    window.currentLiquidityPools = currentLiquidityPools;\n    window.latestLiquiditySweep = null;"
    if target_let_liq in content:
        content = content.replace(target_let_liq, replacement_var_liq)
        print(" [x] Replaced let currentLiquidityPools with var declaration")

    # 3. Defensive check in redrawDrawings
    target_redraw_liq = """        // Institutional Liquidity Pools & Sweep Alerts (ASH, ASL, EQH, EQL)
        if (currentLiquidityPools) {
          drawInstitutionalLiquidityOverlay(drawingCtx, currentLiquidityPools, window.latestLiquiditySweep);
        }"""
    replacement_redraw_liq = """        // Institutional Liquidity Pools & Sweep Alerts (ASH, ASL, EQH, EQL)
        const actLiquidityPools = (typeof currentLiquidityPools !== 'undefined' && currentLiquidityPools) ? currentLiquidityPools : (window.currentLiquidityPools || null);
        if (actLiquidityPools) {
          drawInstitutionalLiquidityOverlay(drawingCtx, actLiquidityPools, window.latestLiquiditySweep);
        }"""
    if target_redraw_liq in content:
        content = content.replace(target_redraw_liq, replacement_redraw_liq)
        print(" [x] Updated redrawDrawings with safe actLiquidityPools access")

    # 4. Safe navigation for shortTermSignalLock in updateActiveSetupCard
    target_sw_lock = """      // 0. REAL-TIME INSTITUTIONAL LIQUIDITY SWEEP PRIORITY UPDATE
      if (window.latestLiquiditySweep && (!shortTermSignalLock.active || shortTermSignalLock.status !== 'ACTIVE_HOLD')) {
        const sw = window.latestLiquiditySweep;
        shortTermSignalLock = {
          active: true,
          signalType: sw.type,
          action: sw.type === 'BUY' ? 'HIGH CONVICTION BUY' : 'HIGH CONVICTION SELL',
          confidence: '95% (Institutional Liquidity Raid)',
          entryPrice: sw.entry,
          tp1: sw.tp,
          tp2: sw.tp + (sw.type === 'BUY' ? 6.0 : -6.0),
          sl: Number(sw.sl),
          rr: sw.rr,
          gainPts: Math.abs(sw.tp - sw.entry),
          reason: sw.reason,
          lockedAt: now,
          maxLockDurationMs: 60 * 60 * 1000,
          status: 'ACTIVE_HOLD',
          completedAt: null,
          lastCompletedType: shortTermSignalLock.lastCompletedType,
          lastCompletedStatus: shortTermSignalLock.lastCompletedStatus
        };
        window.shortTermSignalLock = shortTermSignalLock;
      }"""

    replacement_sw_lock = """      // 0. REAL-TIME INSTITUTIONAL LIQUIDITY SWEEP PRIORITY UPDATE
      const curLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) 
        ? shortTermSignalLock 
        : (window.shortTermSignalLock || null);

      if (window.latestLiquiditySweep && (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD')) {
        const sw = window.latestLiquiditySweep;
        shortTermSignalLock = {
          active: true,
          signalType: sw.type,
          action: sw.type === 'BUY' ? 'HIGH CONVICTION BUY' : 'HIGH CONVICTION SELL',
          confidence: '95% (Institutional Liquidity Raid)',
          entryPrice: sw.entry,
          tp1: sw.tp,
          tp2: sw.tp + (sw.type === 'BUY' ? 6.0 : -6.0),
          sl: Number(sw.sl),
          rr: sw.rr,
          gainPts: Math.abs(sw.tp - sw.entry),
          reason: sw.reason,
          lockedAt: now,
          maxLockDurationMs: 60 * 60 * 1000,
          status: 'ACTIVE_HOLD',
          completedAt: null,
          lastCompletedType: curLock ? curLock.lastCompletedType : null,
          lastCompletedStatus: curLock ? curLock.lastCompletedStatus : null
        };
        window.shortTermSignalLock = shortTermSignalLock;
      }"""

    if target_sw_lock in content:
        content = content.replace(target_sw_lock, replacement_sw_lock)
        print(" [x] Updated updateActiveSetupCard sweep lock with safe curLock check")

    # 5. Safe check for stLiquidityBadge
    target_badge_check = """      // Update 1-Line Liquidity Sweep Confirmation Badge
      const stLiqBadge = document.getElementById('stLiquidityBadge');
      if (stLiqBadge) {
        if (window.latestLiquiditySweep && (shortTermSignalLock.status === 'ACTIVE_HOLD' || shortTermSignalLock.status === 'RUNNER_ACTIVE')) {"""

    replacement_badge_check = """      // Update 1-Line Liquidity Sweep Confirmation Badge
      const stLiqBadge = document.getElementById('stLiquidityBadge');
      if (stLiqBadge) {
        const currentLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) ? shortTermSignalLock : window.shortTermSignalLock;
        if (window.latestLiquiditySweep && currentLock && (currentLock.status === 'ACTIVE_HOLD' || currentLock.status === 'RUNNER_ACTIVE')) {"""

    if target_badge_check in content:
        content = content.replace(target_badge_check, replacement_badge_check)
        print(" [x] Updated stLiquidityBadge check with safe currentLock check")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {filepath} ({len(content):,} bytes).\n")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        fix_file(fn)
