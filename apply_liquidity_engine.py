"""
Implement Comprehensive Institutional Liquidity Engine across
gold_dashboard.html, index.html, and deep_analysis_gold.html.

Covers:
1. HTF & Session Liquidity Tracker:
   - Asia Session (00:00 - 07:00 UTC): ASH & ASL.
   - London Session (07:00 - 13:00 UTC): LSH & LSL.
   - Previous Day High (PDH) & Previous Day Low (PDL).
   - Equal Highs (EQH) & Equal Lows (EQL): 2 or more swing highs/lows within 0.30 USD.
   - Trendline Liquidity Pools.
2. Liquidity Sweep & Raid Detection Logic:
   - Bullish Sweep (pierces below ASL, LSL, PDL, EQL, lower wick >= 40%).
   - Bearish Sweep (spikes above ASH, LSH, PDH, EQH, upper wick >= 40%).
3. Prediction & Target Engine Sync:
   - Magnet Effect: Sets opposing liquidity pool as primary Take Profit (TP).
   - Ghost Candle: 15M Ghost Candle aligns directly to opposing liquidity pool.
   - Liquidity Shield: Instantly kills counter-trend signals approaching un-swept liquidity pools.
4. Ultra-Clean UI Architecture:
   - Background calculations hidden.
   - Clean subtle dotted horizontal lines on chart canvas with badges.
   - "⚡ Liquidity Swept" tag banner.
   - 1-line badge on Execution Signals card ("Confirmed: Asia Low Swept + Demand Absorption").
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

def apply_liquidity_engine(filepath):
    print(f"Upgrading {filepath} with Comprehensive Institutional Liquidity Engine...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # =========================================================================
    # 1. UPGRADE trackInstitutionalLiquidity & detectInstitutionalLiquiditySweeps
    # =========================================================================
    target_engine_start = """    // ==========================================
    // COMPLETE SMC INSTITUTIONAL LIQUIDITY SWEEP ENGINE
    // (Session High/Low, EQH/EQL, Trendline, & Old High/Low)
    // ==========================================
    let currentLiquidityPools = null;
    window.latestLiquiditySweep = null;

    function trackInstitutionalLiquidity(candles) {"""

    # Find where trackInstitutionalLiquidity ends and detectSmartMoneyZones starts
    anchor_end = "    function detectSmartMoneyZones(candles) {"
    if target_engine_start not in content or anchor_end not in content:
        print(" [!] Could not find target_engine_start or anchor_end!")
        return

    start_idx = content.find(target_engine_start)
    end_idx = content.find(anchor_end)

    new_liquidity_engine_code = """    // ==========================================
    // COMPREHENSIVE INSTITUTIONAL LIQUIDITY ENGINE
    // (Session High/Low, PDH/PDL, EQH/EQL, Trendline Sweeps & Magnet Targets)
    // ==========================================
    let currentLiquidityPools = null;
    window.latestLiquiditySweep = null;

    function trackInstitutionalLiquidity(candles) {
      if (!candles || candles.length < 15) return null;

      const currentPrice = (typeof currentLiveSpot !== 'undefined' && currentLiveSpot) 
        ? currentLiveSpot 
        : candles[candles.length - 1].close;

      const currentBar = candles[candles.length - 1];
      const curDt = new Date(currentBar.time * 1000);
      const currentUtcDate = curDt.toISOString().slice(0, 10);

      // 1. Asian Session (00:00 - 07:00 UTC) & London Session (07:00 - 13:00 UTC)
      const todayAsianCandles = [];
      const todayLondonCandles = [];
      const prevDayCandles = [];

      let prevUtcDate = null;
      for (let i = candles.length - 1; i >= 0; i--) {
        const dStr = new Date(candles[i].time * 1000).toISOString().slice(0, 10);
        if (dStr < currentUtcDate) {
          prevUtcDate = dStr;
          break;
        }
      }

      for (let i = candles.length - 1; i >= 0; i--) {
        const c = candles[i];
        const dt = new Date(c.time * 1000);
        const dStr = dt.toISOString().slice(0, 10);
        const h = dt.getUTCHours();

        if (dStr === currentUtcDate) {
          if (h >= 0 && h < 7) todayAsianCandles.push(c);
          else if (h >= 7 && h < 13) todayLondonCandles.push(c);
        } else if (prevUtcDate && dStr === prevUtcDate) {
          prevDayCandles.push(c);
        }
      }

      // Asian Session High / Low (ASH / ASL)
      let asianHigh = 0, asianLow = 0;
      if (todayAsianCandles.length > 0) {
        asianHigh = Math.max(...todayAsianCandles.map(c => c.high));
        asianLow = Math.min(...todayAsianCandles.map(c => c.low));
      } else {
        const recentAsia = candles.filter(c => {
          const h = new Date(c.time * 1000).getUTCHours();
          return h >= 0 && h < 7;
        }).slice(-28);
        if (recentAsia.length) {
          asianHigh = Math.max(...recentAsia.map(c => c.high));
          asianLow = Math.min(...recentAsia.map(c => c.low));
        } else {
          const s = candles.slice(-28, -6);
          asianHigh = Math.max(...s.map(c => c.high));
          asianLow = Math.min(...s.map(c => c.low));
        }
      }

      // London Session High / Low (LSH / LSL)
      let londonHigh = 0, londonLow = 0;
      if (todayLondonCandles.length > 0) {
        londonHigh = Math.max(...todayLondonCandles.map(c => c.high));
        londonLow = Math.min(...todayLondonCandles.map(c => c.low));
      } else {
        const recentLondon = candles.filter(c => {
          const h = new Date(c.time * 1000).getUTCHours();
          return h >= 7 && h < 13;
        }).slice(-24);
        if (recentLondon.length) {
          londonHigh = Math.max(...recentLondon.map(c => c.high));
          londonLow = Math.min(...recentLondon.map(c => c.low));
        }
      }

      // Previous Day High / Low (PDH / PDL)
      let pdh = 0, pdl = 0;
      if (prevDayCandles.length > 5) {
        pdh = Math.max(...prevDayCandles.map(c => c.high));
        pdl = Math.min(...prevDayCandles.map(c => c.low));
      } else {
        const prevDaySlice = candles.slice(-96, -24);
        if (prevDaySlice.length > 10) {
          pdh = Math.max(...prevDaySlice.map(c => c.high));
          pdl = Math.min(...prevDaySlice.map(c => c.low));
        } else {
          pdh = Math.max(...candles.slice(-48, -12).map(c => c.high));
          pdl = Math.min(...candles.slice(-48, -12).map(c => c.low));
        }
      }

      // Previous 4H High / Low (P4HH / P4HL)
      const prev4HSlice = candles.slice(-32, -16);
      const p4hh = prev4HSlice.length ? Math.max(...prev4HSlice.map(c => c.high)) : (pdh - 2.0);
      const p4hl = prev4HSlice.length ? Math.min(...prev4HSlice.map(c => c.low)) : (pdl + 2.0);

      // Equal Highs (EQH) / Equal Lows (EQL): 2 or more swing points within 0.30 USD
      let eqh = null, eql = null;
      const swingHighs = [];
      const swingLows = [];

      for (let i = 2; i < candles.length - 2; i++) {
        const c = candles[i];
        if (c.high > candles[i - 1].high && c.high > candles[i - 2].high &&
            c.high > candles[i + 1].high && c.high > candles[i + 2].high) {
          swingHighs.push({ price: c.high, time: c.time, index: i });
        }
        if (c.low < candles[i - 1].low && c.low < candles[i - 2].low &&
            c.low < candles[i + 1].low && c.low < candles[i + 2].low) {
          swingLows.push({ price: c.low, time: c.time, index: i });
        }
      }

      // Detect Equal Highs within 0.30 USD
      for (let i = swingHighs.length - 1; i >= 1; i--) {
        for (let j = i - 1; j >= Math.max(0, i - 6); j--) {
          if (Math.abs(swingHighs[i].price - swingHighs[j].price) <= 0.30) {
            eqh = Number(((swingHighs[i].price + swingHighs[j].price) / 2).toFixed(2));
            break;
          }
        }
        if (eqh) break;
      }

      // Detect Equal Lows within 0.30 USD
      for (let i = swingLows.length - 1; i >= 1; i--) {
        for (let j = i - 1; j >= Math.max(0, i - 6); j--) {
          if (Math.abs(swingLows[i].price - swingLows[j].price) <= 0.30) {
            eql = Number(((swingLows[i].price + swingLows[j].price) / 2).toFixed(2));
            break;
          }
        }
        if (eql) break;
      }

      // Trendline Liquidity
      let trendlineLowLiquidity = null;
      let trendlineHighLiquidity = null;
      if (swingLows.length >= 2) {
        const l1 = swingLows[swingLows.length - 1];
        const l2 = swingLows[swingLows.length - 2];
        if (l1.price > l2.price) trendlineLowLiquidity = Number(l2.price.toFixed(2));
      }
      if (swingHighs.length >= 2) {
        const h1 = swingHighs[swingHighs.length - 1];
        const h2 = swingHighs[swingHighs.length - 2];
        if (h1.price < h2.price) trendlineHighLiquidity = Number(h2.price.toFixed(2));
      }

      const oldHighSlice = candles.slice(-40, -8);
      const oldHigh = oldHighSlice.length ? Math.max(...oldHighSlice.map(c => c.high)) : (currentPrice + 12);
      const oldLow = oldHighSlice.length ? Math.min(...oldHighSlice.map(c => c.low)) : (currentPrice - 12);

      return {
        asiaHigh: Number(asianHigh.toFixed(2)),
        asiaLow: Number(asianLow.toFixed(2)),
        asianHigh: Number(asianHigh.toFixed(2)),
        asianLow: Number(asianLow.toFixed(2)),
        londonHigh: (londonHigh > 0) ? Number(londonHigh.toFixed(2)) : null,
        londonLow: (londonLow > 0) ? Number(londonLow.toFixed(2)) : null,
        pdh: Number(pdh.toFixed(2)),
        pdl: Number(pdl.toFixed(2)),
        p4hh: Number(p4hh.toFixed(2)),
        p4hl: Number(p4hl.toFixed(2)),
        eqh,
        eql,
        trendlineLowLiquidity,
        trendlineHighLiquidity,
        oldHigh: Number(oldHigh.toFixed(2)),
        oldLow: Number(oldLow.toFixed(2)),
        currentPrice
      };
    }

    // 2. LIQUIDITY SWEEP & RAID DETECTION LOGIC
    function detectInstitutionalLiquiditySweeps(candles, pools) {
      if (!candles || candles.length < 5 || !pools) return null;

      const current = candles[candles.length - 1];
      const prev = candles[candles.length - 2];
      const range = Math.max(0.001, current.high - current.low);
      const lowerWick = Math.min(current.open, current.close) - current.low;
      const upperWick = current.high - Math.max(current.open, current.close);
      const lowerWickRatio = lowerWick / range;
      const upperWickRatio = upperWick / range;

      // Rejection Wick Quality: Lower or Upper wick >= 40% of total candle range
      const isQualityBullWick = lowerWickRatio >= 0.40;
      const isQualityBearWick = upperWickRatio >= 0.40;

      // 1. BULLISH LIQUIDITY SWEEP (LONG TRIGGERS): Pierces below level & closes back ABOVE
      const bullSweepCandidates = [
        { name: "Equal Lows (EQL)", price: pools.eql, code: "EQL" },
        { name: "Asia Session Low (ASL)", price: pools.asiaLow, code: "ASL" },
        { name: "London Session Low (LSL)", price: pools.londonLow, code: "LSL" },
        { name: "Previous Day Low (PDL)", price: pools.pdl, code: "PDL" },
        { name: "Trendline Low", price: pools.trendlineLowLiquidity, code: "TL_LOW" },
        { name: "Old Low", price: pools.oldLow, code: "OLD_LOW" }
      ];

      for (const cand of bullSweepCandidates) {
        if (!cand.price || cand.price <= 0) continue;
        const swept = (current.low < cand.price && current.close > cand.price && isQualityBullWick) ||
                      (prev.low < cand.price && current.close > cand.price);
        if (swept) {
          const sweepLowest = Math.min(current.low, prev.low);
          const entry = Number(current.close.toFixed(2));
          const sl = Number((sweepLowest - 1.50).toFixed(2));
          const risk = Math.max(2.0, entry - sl);

          // MAGNET EFFECT: Set primary TP to opposing liquidity pool above (EQH, ASH, LSH, PDH)
          const targetPool = (pools.eqh && pools.eqh > entry) ? pools.eqh :
                             (pools.asiaHigh && pools.asiaHigh > entry) ? pools.asiaHigh :
                             (pools.londonHigh && pools.londonHigh > entry) ? pools.londonHigh :
                             (pools.pdh && pools.pdh > entry) ? pools.pdh :
                             Number((entry + (risk * 3.5)).toFixed(2));
          const tp = Number(targetPool.toFixed(2));
          const gain = Math.abs(tp - entry);
          const rr = `1 : ${(gain / risk).toFixed(1)}`;

          return {
            type: "BUY",
            verdict: "BUY-SIDE LIQUIDITY EXPANSION / STOP HUNT CONFIRMED",
            levelName: cand.name,
            levelCode: cand.code,
            sweptPrice: cand.price,
            sweepLowest,
            entryPrice: entry,
            entry,
            sl,
            tp,
            takeProfit: tp,
            gainPts: Number(gain.toFixed(1)),
            rr,
            badgeText: `Confirmed: ${cand.name} Swept + Demand Absorption`,
            reason: `${cand.name} ($${cand.price.toFixed(2)}) swept with ${Math.round(lowerWickRatio * 100)}% rejection wick. Smart Money stop hunt complete -> Target opposing liquidity ($${tp.toFixed(1)}).`,
            markerText: `⚡ ${cand.code} SWEPT`
          };
        }
      }

      // 2. BEARISH LIQUIDITY SWEEP (SHORT TRIGGERS): Spikes above level & closes back BELOW
      const bearSweepCandidates = [
        { name: "Equal Highs (EQH)", price: pools.eqh, code: "EQH" },
        { name: "Asia Session High (ASH)", price: pools.asiaHigh, code: "ASH" },
        { name: "London Session High (LSH)", price: pools.londonHigh, code: "LSH" },
        { name: "Previous Day High (PDH)", price: pools.pdh, code: "PDH" },
        { name: "Trendline High", price: pools.trendlineHighLiquidity, code: "TL_HIGH" },
        { name: "Old High", price: pools.oldHigh, code: "OLD_HIGH" }
      ];

      for (const cand of bearSweepCandidates) {
        if (!cand.price || cand.price <= 0) continue;
        const swept = (current.high > cand.price && current.close < cand.price && isQualityBearWick) ||
                      (prev.high > cand.price && current.close < cand.price);
        if (swept) {
          const sweepHighest = Math.max(current.high, prev.high);
          const entry = Number(current.close.toFixed(2));
          const sl = Number((sweepHighest + 1.50).toFixed(2));
          const risk = Math.max(2.0, sl - entry);

          // MAGNET EFFECT: Set primary TP to opposing liquidity pool below (EQL, ASL, LSL, PDL)
          const targetPool = (pools.eql && pools.eql < entry) ? pools.eql :
                             (pools.asiaLow && pools.asiaLow < entry) ? pools.asiaLow :
                             (pools.londonLow && pools.londonLow < entry) ? pools.londonLow :
                             (pools.pdl && pools.pdl < entry) ? pools.pdl :
                             Number((entry - (risk * 3.5)).toFixed(2));
          const tp = Number(targetPool.toFixed(2));
          const gain = Math.abs(entry - tp);
          const rr = `1 : ${(gain / risk).toFixed(1)}`;

          return {
            type: "SELL",
            verdict: "SELL-SIDE LIQUIDITY EXPANSION / HIGH RAID CONFIRMED",
            levelName: cand.name,
            levelCode: cand.code,
            sweptPrice: cand.price,
            sweepHighest,
            entryPrice: entry,
            entry,
            sl,
            tp,
            takeProfit: tp,
            gainPts: Number(gain.toFixed(1)),
            rr,
            badgeText: `Confirmed: ${cand.name} Swept + Supply Defense`,
            reason: `${cand.name} ($${cand.price.toFixed(2)}) swept with ${Math.round(upperWickRatio * 100)}% rejection wick. Buy-stops purged -> Target opposing liquidity ($${tp.toFixed(1)}).`,
            markerText: `⚡ ${cand.code} SWEPT`
          };
        }
      }

      return null;
    }

    // 3. THE LIQUIDITY SHIELD: INSTANTLY KILLS COUNTER-TREND TRADES INTO UN-SWEPT POOLS
    function applyLiquidityShield(proposedAction, currentPrice, pools) {
      if (!pools) return { allowed: true };

      if (proposedAction === 'BUY') {
        const unsweptLows = [
          { name: "Equal Lows (EQL)", price: pools.eql },
          { name: "Asia Low (ASL)", price: pools.asiaLow },
          { name: "London Low (LSL)", price: pools.londonLow },
          { name: "Previous Day Low (PDL)", price: pools.pdl }
        ];
        for (const l of unsweptLows) {
          if (l.price && currentPrice > l.price && (currentPrice - l.price) <= 3.20) {
            return {
              allowed: false,
              reason: `Rule 0.1 Liquidity Shield: Un-swept ${l.name} at $${l.price.toFixed(2)} nearby. Smart Money will hunt sell-stops first before rally.`,
              poolLevel: l.price
            };
          }
        }
      }

      if (proposedAction === 'SELL') {
        const unsweptHighs = [
          { name: "Equal Highs (EQH)", price: pools.eqh },
          { name: "Asia High (ASH)", price: pools.asiaHigh },
          { name: "London High (LSH)", price: pools.londonHigh },
          { name: "Previous Day High (PDH)", price: pools.pdh }
        ];
        for (const h of unsweptHighs) {
          if (h.price && currentPrice < h.price && (h.price - currentPrice) <= 3.20) {
            return {
              allowed: false,
              reason: `Rule 0.1 Liquidity Shield: Un-swept ${h.name} at $${h.price.toFixed(2)} nearby. Smart Money will raid buy-stops first before drop.`,
              poolLevel: h.price
            };
          }
        }
      }

      return { allowed: true };
    }

    // 4. CANVAS OVERLAY FOR INSTITUTIONAL LIQUIDITY POOLS (Clean, Subtle Dotted Lines & Tags)
    function drawInstitutionalLiquidityOverlay(ctx, pools, activeSweep) {
      if (!pools || !ctx || !candleSeries || !chart) return;

      ctx.save();

      const levelsToDraw = [
        { label: 'Asia High (ASH)', desc: 'Asia High', price: pools.asiaHigh, color: 'rgba(255, 215, 0, 0.50)', textColor: '#ffd700' },
        { label: 'Asia Low (ASL)', desc: 'Asia Low', price: pools.asiaLow, color: 'rgba(88, 166, 255, 0.50)', textColor: '#58a6ff' },
      ];

      if (pools.londonHigh) {
        levelsToDraw.push({ label: 'London High (LSH)', desc: 'London High', price: pools.londonHigh, color: 'rgba(240, 140, 0, 0.50)', textColor: '#f08c00' });
      }
      if (pools.londonLow) {
        levelsToDraw.push({ label: 'London Low (LSL)', desc: 'London Low', price: pools.londonLow, color: 'rgba(0, 180, 216, 0.50)', textColor: '#00b4d8' });
      }
      if (pools.pdh) {
        levelsToDraw.push({ label: 'PDH', desc: 'Prev Day High', price: pools.pdh, color: 'rgba(163, 113, 247, 0.50)', textColor: '#a371f7' });
      }
      if (pools.pdl) {
        levelsToDraw.push({ label: 'PDL', desc: 'Prev Day Low', price: pools.pdl, color: 'rgba(163, 113, 247, 0.50)', textColor: '#a371f7' });
      }
      if (pools.eqh) {
        levelsToDraw.push({ label: 'Equal Highs (EQH)', desc: 'Buy-Side Liquidity', price: pools.eqh, color: 'rgba(248, 81, 73, 0.55)', textColor: '#f85149' });
      }
      if (pools.eql) {
        levelsToDraw.push({ label: 'Equal Lows (EQL)', desc: 'Sell-Side Liquidity', price: pools.eql, color: 'rgba(63, 185, 80, 0.55)', textColor: '#3fb950' });
      }

      levelsToDraw.forEach(lvl => {
        if (!lvl.price || lvl.price <= 0) return;
        const y = candleSeries.priceToCoordinate(lvl.price);
        if (y === null || y < 0 || y > canvasCssHeight) return;

        // Subtle, fine dotted line
        ctx.strokeStyle = lvl.color;
        ctx.lineWidth = 1;
        ctx.setLineDash([2, 4]);
        ctx.beginPath();
        ctx.moveTo(15, y);
        ctx.lineTo(canvasCssWidth - 65, y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Small clean tag badge on the right
        const txt = `${lvl.label} · $${lvl.price.toFixed(1)} [Liquidity Pool]`;
        ctx.font = '600 8.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        const w = ctx.measureText(txt).width + 8;
        const tagX = canvasCssWidth - w - 70;

        ctx.fillStyle = 'rgba(13, 17, 23, 0.88)';
        ctx.fillRect(tagX, y - 7, w, 14);
        ctx.strokeStyle = lvl.color;
        ctx.strokeRect(tagX, y - 7, w, 14);

        ctx.fillStyle = lvl.textColor;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        ctx.fillText(txt, tagX + 4, y);
      });

      // Flash subtle "⚡ Liquidity Swept" marker when a sweep is confirmed
      if (activeSweep && activeSweep.sweepLowest || (activeSweep && activeSweep.sweptPrice)) {
        const sweepPrice = activeSweep.sweptPrice || activeSweep.sweepLowest;
        const sweepY = candleSeries.priceToCoordinate(sweepPrice);
        if (sweepY !== null && sweepY >= 0 && sweepY <= canvasCssHeight) {
          const bannerTxt = `⚡ Liquidity Swept: ${activeSweep.levelName} (${activeSweep.type === 'BUY' ? 'Demand Absorption' : 'Supply Defense'})`;
          ctx.font = '800 10.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const bannerW = ctx.measureText(bannerTxt).width + 16;
          const bannerX = Math.round(canvasCssWidth / 2 - (bannerW / 2));
          const bannerY = Math.max(10, Math.min(canvasCssHeight - 25, sweepY - 12));

          ctx.fillStyle = activeSweep.type === 'BUY' ? 'rgba(46, 160, 67, 0.95)' : 'rgba(248, 81, 73, 0.95)';
          ctx.beginPath();
          if (ctx.roundRect) ctx.roundRect(bannerX, bannerY, bannerW, 22, 5);
          else ctx.rect(bannerX, bannerY, bannerW, 22);
          ctx.fill();

          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1;
          ctx.stroke();

          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(bannerTxt, bannerX + (bannerW / 2), bannerY + 11);
        }
      }

      ctx.restore();
    }
\n"""

    content = content[:start_idx] + new_liquidity_engine_code + content[end_idx:]
    print(" [x] Injected Comprehensive Institutional Liquidity Engine.")

    # =========================================================================
    # 2. INJECT LIQUIDITY SHIELD IN evaluateHighAccuracySetup
    # =========================================================================
    target_shield_anchor = """      // Priority 0: CONFIRMED INSTITUTIONAL LIQUIDITY SWEEP (MANDATORY EXECUTION)
      if (activeSweep) {
        if (activeSweep.type === 'BUY') {
          buyVotes += 4.5;
          institutionalBuyTrigger = true;
          agent1Bias = 'LIQUIDITY_RAID_BUY';
          agent1Desc = activeSweep.reason;
        } else {
          sellVotes += 4.5;
          supplyRejectionWarning = true;
          agent1Bias = 'LIQUIDITY_RAID_SELL';
          agent1Desc = activeSweep.reason;
        }
      }"""

    replacement_shield_anchor = """      // Priority 0: CONFIRMED INSTITUTIONAL LIQUIDITY SWEEP (MANDATORY EXECUTION)
      if (activeSweep) {
        if (activeSweep.type === 'BUY') {
          buyVotes += 5.0;
          institutionalBuyTrigger = true;
          agent1Bias = 'LIQUIDITY_RAID_BUY';
          agent1Desc = activeSweep.reason;
        } else {
          sellVotes += 5.0;
          supplyRejectionWarning = true;
          agent1Bias = 'LIQUIDITY_RAID_SELL';
          agent1Desc = activeSweep.reason;
        }
      }

      // RULE 0.1: THE LIQUIDITY SHIELD (Instantly kill counter-trend trades approaching un-swept liquidity)
      const shieldCheckBuy = applyLiquidityShield('BUY', currentPrice, currentLiquidityPools);
      const shieldCheckSell = applyLiquidityShield('SELL', currentPrice, currentLiquidityPools);
      if (!shieldCheckBuy.allowed && !activeSweep) {
        buyVotes = 0; // KILL COUNTER-TREND BUY!
      }
      if (!shieldCheckSell.allowed && !activeSweep) {
        sellVotes = 0; // KILL COUNTER-TREND SELL!
      }"""

    if target_shield_anchor in content:
        content = content.replace(target_shield_anchor, replacement_shield_anchor)
        print(" [x] Enforced Liquidity Shield counter-trend kill rule in evaluateHighAccuracySetup.")
    else:
        print(" [!] Could not find target_shield_anchor.")

    # =========================================================================
    # 3. SYNCHRONIZE 15M GHOST CANDLE WITH OPPOSING LIQUIDITY POOL
    # =========================================================================
    target_ghost_anchor = """      // Candlestick Pattern Trajectory Confluence & Next Candle Prediction"""
    ghost_sweep_sync = """      // INSTITUTIONAL LIQUIDITY SWEEP TRAJECTORY CONFLUENCE (Priority Magnet Target)
      if (window.latestLiquiditySweep) {
        const sw = window.latestLiquiditySweep;
        isUp = (sw.type === 'BUY');
        const tpVal = Number(sw.tp);
        targetLabel = `🎯 Opposing Pool $${tpVal.toFixed(1)} (${sw.levelCode || 'Sweep'})`;
        targetColor = isUp ? '#2ea043' : '#f85149';

        if (isUp) {
          c1_open = currentPrice;
          c1_close = c1_open + (atr * 1.2);
          c1_high = c1_close + (atr * 0.35);
          c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close;
          c2_close = c2_open + (atr * 1.4);
          c2_high = c2_close + (atr * 0.40);
          c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close;
          c3_close = tpVal;
          c3_high = c3_close + (atr * 0.35);
          c3_low = c3_open - (atr * 0.20);
        } else {
          c1_open = currentPrice;
          c1_close = c1_open - (atr * 1.2);
          c1_low = c1_close - (atr * 0.35);
          c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close;
          c2_close = c2_open - (atr * 1.4);
          c2_low = c2_close - (atr * 0.40);
          c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close;
          c3_close = tpVal;
          c3_low = c3_close - (atr * 0.35);
          c3_high = c3_open + (atr * 0.20);
        }

        // STRICT SYNC TO CARD
        if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) {
          shortTermSignalLock.tp1 = tpVal;
          shortTermSignalLock.gainPts = Number(Math.abs(tpVal - shortTermSignalLock.entryPrice).toFixed(1));
          const risk = Math.max(2.0, Math.abs(shortTermSignalLock.entryPrice - shortTermSignalLock.sl));
          shortTermSignalLock.rrText = `1 : ${(shortTermSignalLock.gainPts / risk).toFixed(1)} (+${shortTermSignalLock.gainPts.toFixed(1)} pts)`;

          const stTp = document.getElementById('stTpVal');
          const stRr = document.getElementById('stRrVal');
          if (stTp) stTp.innerText = '$' + tpVal.toFixed(2);
          if (stRr) stRr.innerText = shortTermSignalLock.rrText;
        }
      }

      """

    if target_ghost_anchor in content and "INSTITUTIONAL LIQUIDITY SWEEP TRAJECTORY CONFLUENCE" not in content:
        content = content.replace(target_ghost_anchor, ghost_sweep_sync + target_ghost_anchor)
        print(" [x] Aligned 15M Ghost Candle to Opposing Liquidity Target.")

    # =========================================================================
    # 4. EXECUTION SIGNALS CARD 1-LINE BADGE (HTML + JS UPDATE)
    # =========================================================================
    target_card_html = """            <!-- Single Crisp 1-Line Reason -->
            <div id="stNoteVal" class="clean-signal-note" style="font-size: 10.5px; padding: 6px 9px;">
              Safe-haven capital flow breaking through local supply.
            </div>"""

    replacement_card_html = """            <!-- Single Crisp 1-Line Reason -->
            <div id="stNoteVal" class="clean-signal-note" style="font-size: 10.5px; padding: 6px 9px;">
              Safe-haven capital flow breaking through local supply.
            </div>

            <!-- 1-Line Liquidity Sweep Confirmation Badge -->
            <div id="stLiquidityBadge" class="clean-signal-note" style="display: none; margin-top: 6px; font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 5px; text-align: center; border: 1px solid rgba(255, 215, 0, 0.35); background: rgba(255, 215, 0, 0.08); color: #ffd700;">
              Confirmed: Asia Low Swept + Demand Absorption
            </div>"""

    if target_card_html in content:
        content = content.replace(target_card_html, replacement_card_html)
        print(" [x] Added stLiquidityBadge HTML element to Intraday Bento card.")
    else:
        print(" [!] Could not find exact target_card_html.")

    # JS update in updateActiveSetupCard for stLiquidityBadge
    target_st_note_js = """      if (stNote) {
        if (shortTermSignalLock.status === 'TP_HIT') {
          stNote.innerText = 'Target reached · Lock profit or trail stop to breakeven.';
          stNote.style.color = '#3fb950';
        } else if (shortTermSignalLock.status === 'SL_HIT') {
          stNote.innerText = 'SETUP INVALIDATED / STOPPED OUT -> SEARCHING FOR NEXT ZONE';
          stNote.style.color = '#f85149';
        } else {
          stNote.innerText = shortTermSignalLock.reason;
          stNote.style.color = '';
        }
      }"""

    replacement_st_note_js = """      if (stNote) {
        if (shortTermSignalLock.status === 'TP_HIT') {
          stNote.innerText = 'Target reached · Lock profit or trail stop to breakeven.';
          stNote.style.color = '#3fb950';
        } else if (shortTermSignalLock.status === 'SL_HIT') {
          stNote.innerText = 'SETUP INVALIDATED / STOPPED OUT -> SEARCHING FOR NEXT ZONE';
          stNote.style.color = '#f85149';
        } else {
          stNote.innerText = shortTermSignalLock.reason;
          stNote.style.color = '';
        }
      }

      // Update 1-Line Liquidity Sweep Confirmation Badge
      const stLiqBadge = document.getElementById('stLiquidityBadge');
      if (stLiqBadge) {
        if (window.latestLiquiditySweep && (shortTermSignalLock.status === 'ACTIVE_HOLD' || shortTermSignalLock.status === 'RUNNER_ACTIVE')) {
          stLiqBadge.innerText = window.latestLiquiditySweep.badgeText || `Confirmed: ${window.latestLiquiditySweep.levelName} Swept + Absorption`;
          stLiqBadge.style.display = 'block';
          if (window.latestLiquiditySweep.type === 'BUY') {
            stLiqBadge.style.background = 'rgba(46, 160, 67, 0.12)';
            stLiqBadge.style.color = '#3fb950';
            stLiqBadge.style.borderColor = 'rgba(46, 160, 67, 0.35)';
          } else {
            stLiqBadge.style.background = 'rgba(248, 81, 73, 0.12)';
            stLiqBadge.style.color = '#f85149';
            stLiqBadge.style.borderColor = 'rgba(248, 81, 73, 0.35)';
          }
        } else {
          stLiqBadge.style.display = 'none';
        }
      }"""

    if target_st_note_js in content:
        content = content.replace(target_st_note_js, replacement_st_note_js)
        print(" [x] Wired stLiquidityBadge display in updateActiveSetupCard.")
    else:
        print(" [!] Could not find target_st_note_js.")

    # Ensure drawInstitutionalLiquidityOverlay is always called in redrawDrawings
    old_redraw_call = """        // Institutional Liquidity Pools & Sweep Alerts (ASH, ASL, EQH, EQL)
        if (currentLiquidityPools) {
          drawInstitutionalLiquidityOverlay(drawingCtx, currentLiquidityPools, window.latestLiquiditySweep);
        }"""

    # We want it to be called cleanly in redrawDrawings
    if old_redraw_call in content:
        print(" [x] drawInstitutionalLiquidityOverlay is properly hooked in redrawDrawings.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {filepath} ({len(content):,} bytes).\n")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        apply_liquidity_engine(fn)
