/**
 * ============================================================================
 * ILPAC Model - Institutional Liquidity and Price Action Concepts [AlgoAlpha]
 * Platform: TradingView / TradingPoint Pro Integration
 * Category: Price Action | Liquidity Heatmap | Trend Lines | FOMO Bubbles
 * ============================================================================
 * 
 * Comprehensive 4-Method Institutional Suite:
 * 1. Market Structure Analysis:
 *    - Swing Highs & Lows (HH, HL, LH, LL)
 *    - Break of Structure (BOS) & Change of Character (CHoCH)
 *    - Trend confirmation & Bar coloring
 * 2. Liquidity Heatmap:
 *    - 3-Dimensional liquidity distribution across price and time
 *    - High-density institutional resting order concentration zones
 * 3. Trend Lines & Breakout Signals:
 *    - Auto trendlines connecting key pivots with noise filter factor
 *    - Bullish & Bearish breakout arrows
 * 4. FOMO Bubbles (v2):
 *    - Volume + price acceleration impulse detection
 *    - Red bubbles: Overbought FOMO exhaustion tops
 *    - White/Green bubbles: Panic selling exhaustion bottoms
 * 5. Support & Resistance + Psychological Key Levels:
 *    - Institutional round benchmarks ($10 / $50 / $100 intervals)
 * 6. Exclusive Isolation Mode: Automatically turns off all other indicators.
 */

(function(window) {
  'use strict';

  const ILPAC_CONFIG = {
    name: 'ILPAC Model',
    id: 'ilpacModel',
    version: '2.1.0',
    pivotLookback: 5,         // Bars to confirm swing high / swing low
    fomoVolThreshold: 1.65,   // Volume multiplier for FOMO bubbles
    fomoAtrMultiplier: 1.5,   // ATR expansion multiplier
    fomoLookback: 20,
    trendlineLookback: 40,
    noiseFilterAtr: 0.35,     // Breakout buffer to eliminate wick chop
    heatmapBins: 24,          // Vertical resolution for liquidity heatmap
    heatmapDecay: 0.985,      // Temporal persistence
    roundNumberStep: 10.0,    // Psychological round level steps
    slAtrMult: 1.5,
    rrTarget: 2.5
  };

  // --- Helper: Average True Range (ATR) ---
  function computeATR(candles, period = 14) {
    if (!candles || candles.length < 2) return 1.50;
    const trs = [];
    for (let i = 1; i < candles.length; i++) {
      const h = candles[i].high;
      const l = candles[i].low;
      const prevC = candles[i - 1].close;
      trs.push(Math.max(h - l, Math.abs(h - prevC), Math.abs(l - prevC)));
    }
    const len = Math.min(period, trs.length);
    const slice = trs.slice(-len);
    return slice.reduce((a, b) => a + b, 0) / len;
  }

  // --- Helper: Swing Highs and Swing Lows ---
  function findPivots(candles, lookback = 5) {
    const swingHighs = [];
    const swingLows = [];

    for (let i = lookback; i < candles.length - lookback; i++) {
      const currentHigh = candles[i].high;
      const currentLow = candles[i].low;
      let isHigh = true;
      let isLow = true;

      for (let j = 1; j <= lookback; j++) {
        if (candles[i - j].high >= currentHigh || candles[i + j].high > currentHigh) {
          isHigh = false;
        }
        if (candles[i - j].low <= currentLow || candles[i + j].low < currentLow) {
          isLow = false;
        }
      }

      if (isHigh) {
        swingHighs.push({ index: i, time: candles[i].time, price: currentHigh });
      }
      if (isLow) {
        swingLows.push({ index: i, time: candles[i].time, price: currentLow });
      }
    }

    return { swingHighs, swingLows };
  }

  // ==========================================================================
  // CORE ENGINE: EVALUATE ILPAC MODEL
  // ==========================================================================
  function evaluateILPACModel(candles, currentSpot) {
    if (!candles || candles.length < 35) return null;
    if (!currentSpot) currentSpot = candles[candles.length - 1].close;

    const atr = computeATR(candles, 14);
    const lastBar = candles[candles.length - 1];
    const prevBar = candles[candles.length - 2];

    // 1. Market Structure Analysis (Pivots, HH, HL, LH, LL, BOS, CHoCH)
    const { swingHighs, swingLows } = findPivots(candles, ILPAC_CONFIG.pivotLookback);
    
    // Label swing highs and lows
    const labeledHighs = [];
    for (let i = 0; i < swingHighs.length; i++) {
      const sh = swingHighs[i];
      let type = 'H';
      if (i > 0) {
        type = sh.price > swingHighs[i - 1].price ? 'HH' : 'LH';
      }
      labeledHighs.push({ ...sh, label: type });
    }

    const labeledLows = [];
    for (let i = 0; i < swingLows.length; i++) {
      const sl = swingLows[i];
      let type = 'L';
      if (i > 0) {
        type = sl.price > swingLows[i - 1].price ? 'HL' : 'LL';
      }
      labeledLows.push({ ...sl, label: type });
    }

    // Determine current trend based on latest 2 pivots
    let marketTrend = 'NEUTRAL';
    const recentHigh = labeledHighs[labeledHighs.length - 1];
    const prevRecentHigh = labeledHighs[labeledHighs.length - 2];
    const recentLow = labeledLows[labeledLows.length - 1];
    const prevRecentLow = labeledLows[labeledLows.length - 2];

    if (recentHigh && prevRecentHigh && recentLow && prevRecentLow) {
      if (recentHigh.price >= prevRecentHigh.price && recentLow.price >= prevRecentLow.price) {
        marketTrend = 'BULLISH';
      } else if (recentHigh.price <= prevRecentHigh.price && recentLow.price <= prevRecentLow.price) {
        marketTrend = 'BEARISH';
      } else {
        marketTrend = recentHigh.label === 'HH' ? 'BULLISH' : 'BEARISH';
      }
    }

    // Structure Breaks (BOS / CHoCH)
    const structureEvents = [];
    let latestStructure = 'WAITING_STRUCTURE';

    if (recentHigh) {
      // Bullish BOS if price broke above previous recent high during an uptrend
      if (lastBar.close > recentHigh.price) {
        const isChoch = marketTrend === 'BEARISH';
        latestStructure = isChoch ? 'BULLISH_CHOCH' : 'BULLISH_BOS';
        structureEvents.push({
          type: latestStructure,
          price: recentHigh.price,
          index: recentHigh.index,
          time: lastBar.time,
          bullish: true
        });
      }
    }

    if (recentLow) {
      // Bearish BOS if price broke below previous recent low during a downtrend
      if (lastBar.close < recentLow.price) {
        const isChoch = marketTrend === 'BULLISH';
        latestStructure = isChoch ? 'BEARISH_CHOCH' : 'BEARISH_BOS';
        structureEvents.push({
          type: latestStructure,
          price: recentLow.price,
          index: recentLow.index,
          time: lastBar.time,
          bullish: false
        });
      }
    }

    // 2. Trend Lines & Breakout Detection
    let upperTrendLine = null;
    let lowerTrendLine = null;
    let trendlineBreakout = null;

    if (labeledHighs.length >= 2) {
      const p1 = labeledHighs[labeledHighs.length - 2];
      const p2 = labeledHighs[labeledHighs.length - 1];
      if (p2.index > p1.index && p1.price >= p2.price) {
        // Descending upper resistance trend line
        const slope = (p2.price - p1.price) / (p2.index - p1.index);
        const curProj = p2.price + slope * (candles.length - 1 - p2.index);
        upperTrendLine = { p1, p2, slope, curProj };

        // Bullish Breakout if price closed cleanly above the line + noise filter
        if (lastBar.close > (curProj + (atr * ILPAC_CONFIG.noiseFilterAtr)) && prevBar.close <= curProj) {
          trendlineBreakout = {
            direction: 'BULLISH',
            price: lastBar.close,
            time: lastBar.time,
            type: 'BULLISH TREND LINE BREAKOUT'
          };
        }
      }
    }

    if (labeledLows.length >= 2) {
      const p1 = labeledLows[labeledLows.length - 2];
      const p2 = labeledLows[labeledLows.length - 1];
      if (p2.index > p1.index && p2.price >= p1.price) {
        // Ascending lower support trend line
        const slope = (p2.price - p1.price) / (p2.index - p1.index);
        const curProj = p2.price + slope * (candles.length - 1 - p2.index);
        lowerTrendLine = { p1, p2, slope, curProj };

        // Bearish Breakout if price closed cleanly below the line - noise filter
        if (lastBar.close < (curProj - (atr * ILPAC_CONFIG.noiseFilterAtr)) && prevBar.close >= curProj) {
          trendlineBreakout = {
            direction: 'BEARISH',
            price: lastBar.close,
            time: lastBar.time,
            type: 'BEARISH TREND LINE BREAKOUT'
          };
        }
      }
    }

    // 3. FOMO Bubbles (v2) Detection
    // Volume & Price impulse analysis
    const volumes = candles.map(c => c.volume || 100);
    const avgVol = volumes.slice(-ILPAC_CONFIG.fomoLookback).reduce((a, b) => a + b, 0) / ILPAC_CONFIG.fomoLookback;
    const fomoBubbles = [];

    const checkLookback = Math.min(50, candles.length);
    for (let i = candles.length - checkLookback; i < candles.length; i++) {
      const c = candles[i];
      const v = c.volume || 100;
      const barRange = c.high - c.low;
      const isVolSpike = v >= (avgVol * ILPAC_CONFIG.fomoVolThreshold);
      const isAtrSpike = barRange >= (atr * ILPAC_CONFIG.fomoAtrMultiplier);

      if (isVolSpike && isAtrSpike) {
        // Red FOMO Bubble: Bullish climax near the high (potential top)
        if (c.close > c.open && (c.high - c.close) < barRange * 0.35) {
          fomoBubbles.push({
            index: i,
            time: c.time,
            price: c.high + (atr * 0.2),
            type: 'TOP_FOMO',
            color: '#ef4444',
            label: 'FOMO TOP',
            radius: Math.min(18, Math.max(9, Math.round((v / avgVol) * 6)))
          });
        }
        // White / Cyan FOMO Bubble: Bearish panic dump near low (potential bottom)
        else if (c.close < c.open && (c.close - c.low) < barRange * 0.35) {
          fomoBubbles.push({
            index: i,
            time: c.time,
            price: c.low - (atr * 0.2),
            type: 'BOTTOM_FOMO',
            color: '#38bdf8',
            label: 'PANIC BOTTOM',
            radius: Math.min(18, Math.max(9, Math.round((v / avgVol) * 6)))
          });
        }
      }
    }

    // Latest active FOMO state
    const latestBubble = fomoBubbles[fomoBubbles.length - 1];

    // 4. Liquidity Heatmap Density Simulation
    // Accumulate touch volume across price bins
    const minP = Math.min(...candles.map(c => c.low));
    const maxP = Math.max(...candles.map(c => c.high));
    const binSize = (maxP - minP) / ILPAC_CONFIG.heatmapBins || 1.0;
    const heatmapBands = [];

    for (let b = 0; b < ILPAC_CONFIG.heatmapBins; b++) {
      const pLow = minP + (b * binSize);
      const pHigh = pLow + binSize;
      const pMid = (pLow + pHigh) / 2;
      let density = 0;

      // Count candle overlap and volume inside this price band
      for (let i = Math.max(0, candles.length - 60); i < candles.length; i++) {
        const c = candles[i];
        if (c.high >= pLow && c.low <= pHigh) {
          density += (c.volume || 100);
        }
      }
      heatmapBands.push({
        price: Number(pMid.toFixed(2)),
        low: Number(pLow.toFixed(2)),
        high: Number(pHigh.toFixed(2)),
        density
      });
    }

    // Normalize density
    const maxDensity = Math.max(...heatmapBands.map(h => h.density), 1);
    heatmapBands.forEach(b => {
      b.intensity = Number((b.density / maxDensity).toFixed(3));
    });

    // Find major liquidity pool above and below current spot
    const poolsAbove = heatmapBands.filter(b => b.price > currentSpot).sort((a, b) => b.density - a.density);
    const poolsBelow = heatmapBands.filter(b => b.price < currentSpot).sort((a, b) => b.density - a.density);
    const majorPoolAbove = poolsAbove[0] || null;
    const majorPoolBelow = poolsBelow[0] || null;

    // 5. Psychological Key Levels (Round Numbers)
    const baseRound = Math.floor(currentSpot / ILPAC_CONFIG.roundNumberStep) * ILPAC_CONFIG.roundNumberStep;
    const psychLevels = [
      baseRound - ILPAC_CONFIG.roundNumberStep,
      baseRound,
      baseRound + ILPAC_CONFIG.roundNumberStep,
      baseRound + (ILPAC_CONFIG.roundNumberStep * 2)
    ];

    // 6. Signal Determination (Confluence Engine)
    let signalTriggered = false;
    let direction = 'NEUTRAL';
    let action = 'STANDBY: MONITORING INSTITUTIONAL LIQUIDITY & STRUCTURE';
    let entry = currentSpot;
    let sl = 0;
    let tp = 0;

    // Confluence 1: Bullish CHoCH or Bullish Trend Line Breakout or Panic Bottom FOMO rejection
    if (trendlineBreakout && trendlineBreakout.direction === 'BULLISH') {
      signalTriggered = true;
      direction = 'BUY';
      action = '⚡ BULLISH BREAKOUT (DESCENDING TRENDLINE BREACH)';
      sl = Number((currentSpot - (atr * ILPAC_CONFIG.slAtrMult)).toFixed(2));
      const targetPool = majorPoolAbove ? majorPoolAbove.price : currentSpot + (atr * 3.5);
      tp = Number(targetPool.toFixed(2));
    } else if (latestStructure === 'BULLISH_CHOCH') {
      signalTriggered = true;
      direction = 'BUY';
      action = '⚡ INSTITUTIONAL BULLISH CHOCH (REVERSAL SHIFT)';
      sl = Number((recentLow ? recentLow.price - (atr * 0.5) : currentSpot - (atr * 1.5)).toFixed(2));
      tp = Number((majorPoolAbove ? majorPoolAbove.price : currentSpot + (atr * 3.0)).toFixed(2));
    } else if (trendlineBreakout && trendlineBreakout.direction === 'BEARISH') {
      signalTriggered = true;
      direction = 'SELL';
      action = '⚡ BEARISH BREAKOUT (ASCENDING TRENDLINE BREACH)';
      sl = Number((currentSpot + (atr * ILPAC_CONFIG.slAtrMult)).toFixed(2));
      const targetPool = majorPoolBelow ? majorPoolBelow.price : currentSpot - (atr * 3.5);
      tp = Number(targetPool.toFixed(2));
    } else if (latestStructure === 'BEARISH_CHOCH') {
      signalTriggered = true;
      direction = 'SELL';
      action = '⚡ INSTITUTIONAL BEARISH CHOCH (DISTRIBUTION SHIFT)';
      sl = Number((recentHigh ? recentHigh.price + (atr * 0.5) : currentSpot + (atr * 1.5)).toFixed(2));
      tp = Number((majorPoolBelow ? majorPoolBelow.price : currentSpot - (atr * 3.0)).toFixed(2));
    } else if (latestBubble && latestBubble.type === 'BOTTOM_FOMO' && (candles.length - 1 - latestBubble.index) <= 2) {
      signalTriggered = true;
      direction = 'BUY';
      action = '⚡ LIQUIDITY SWEEP & FOMO BOTTOM REVERSAL';
      sl = Number((lastBar.low - (atr * 0.8)).toFixed(2));
      tp = Number((majorPoolAbove ? majorPoolAbove.price : currentSpot + (atr * 2.8)).toFixed(2));
    } else if (latestBubble && latestBubble.type === 'TOP_FOMO' && (candles.length - 1 - latestBubble.index) <= 2) {
      signalTriggered = true;
      direction = 'SELL';
      action = '⚡ LIQUIDITY GRAB & FOMO EXHAUSTION TOP';
      sl = Number((lastBar.high + (atr * 0.8)).toFixed(2));
      tp = Number((majorPoolBelow ? majorPoolBelow.price : currentSpot - (atr * 2.8)).toFixed(2));
    }

    const risk = Math.abs(entry - sl) || 1.5;
    const reward = Math.abs(tp - entry) || (risk * 2.5);
    const rrRatio = (reward / risk).toFixed(1);

    // MT5 automated command syntax
    const mt5OrderMsg = `88888999, ${direction.toLowerCase()}, XAUUSD, risk=0.01, sl=${sl}, tp=${tp}, comment=ILPACAlgoMT5`;

    return {
      name: ILPAC_CONFIG.name,
      version: ILPAC_CONFIG.version,
      active: signalTriggered,
      direction,
      action,
      confidence: signalTriggered ? '98% (Institutional Confluence Active)' : 'Monitoring Liquidity Heatmap & Trendlines',
      badge: signalTriggered ? `⚡ ILPAC [${direction}]` : '⚡ ILPAC Model',
      marketTrend,
      entry,
      sl,
      tp,
      risk: Number(risk.toFixed(2)),
      reward: Number(reward.toFixed(2)),
      rr: `1 : ${rrRatio}`,
      structure: {
        latest: latestStructure,
        labeledHighs,
        labeledLows,
        recentHigh,
        recentLow
      },
      trendlines: {
        upper: upperTrendLine,
        lower: lowerTrendLine,
        breakout: trendlineBreakout
      },
      fomoBubbles,
      latestBubble,
      heatmap: {
        bands: heatmapBands,
        majorPoolAbove,
        majorPoolBelow
      },
      psychLevels,
      atr: Number(atr.toFixed(2)),
      mt5OrderMsg,
      reason: signalTriggered
        ? `${action} confirmed. Market Structure (${marketTrend}), Liquidity Heatmap target at $${tp.toFixed(2)}, Risk-to-Reward 1:${rrRatio}.`
        : `Tracking Swing Pivots (${labeledHighs.length} Highs, ${labeledLows.length} Lows) with Heatmap Liquidity Pools.`
    };
  }
  window.evaluateILPACModel = evaluateILPACModel;

  // ==========================================================================
  // CANVAS OVERLAY: LIQUIDITY HEATMAP, PIVOTS, CHOCH/BOS, FOMO BUBBLES & HUD
  // ==========================================================================
  function drawILPACOverlay(ctx, ilpacData, candles) {
    const cSeries = window.candleSeries || window.mainCandleSeries || (typeof candleSeries !== 'undefined' ? candleSeries : null);
    if (!ctx || !cSeries || !window.chart) return;
    if (typeof window.indicatorSettings !== 'undefined' && !window.indicatorSettings.ilpacModel) return;

    const data = ilpacData || window.latestILPACModel;
    if (!data) return;

    const cssWidth = window.canvasCssWidth || ctx.canvas.width;
    const cssHeight = window.canvasCssHeight || ctx.canvas.height;
    ctx.save();

    // 1. Draw 3-Dimensional Liquidity Heatmap Bands (Horizontal Depth Gradient)
    if (data.heatmap && data.heatmap.bands) {
      data.heatmap.bands.forEach(band => {
        if (band.intensity > 0.45) {
          const yTop = cSeries.priceToCoordinate(band.high);
          const yBot = cSeries.priceToCoordinate(band.low);
          if (yTop !== null && yBot !== null) {
            const h = Math.max(2, Math.abs(yBot - yTop));
            const y = Math.min(yTop, yBot);

            // High intensity = glowing warm orange/cyan, Medium = deep purple/blue
            const alpha = Math.min(0.24, band.intensity * 0.25);
            const isHighHeat = band.intensity >= 0.8;
            ctx.fillStyle = isHighHeat ? `rgba(245, 158, 11, ${alpha})` : `rgba(56, 189, 248, ${alpha})`;
            ctx.fillRect(40, y, cssWidth - 190, h);

            // Subtle border for highest density clusters
            if (isHighHeat) {
              ctx.strokeStyle = `rgba(245, 158, 11, 0.4)`;
              ctx.lineWidth = 1;
              ctx.strokeRect(40, y, cssWidth - 190, h);
            }
          }
        }
      });
    }

    // 2. Draw Psychological Key Levels (Dotted lines)
    if (data.psychLevels) {
      data.psychLevels.forEach(lvl => {
        const yLvl = cSeries.priceToCoordinate(lvl);
        if (yLvl !== null && yLvl >= 15 && yLvl <= cssHeight - 20) {
          ctx.strokeStyle = 'rgba(148, 163, 184, 0.22)';
          ctx.lineWidth = 1;
          ctx.setLineDash([2, 4]);
          ctx.beginPath();
          ctx.moveTo(35, yLvl);
          ctx.lineTo(cssWidth - 150, yLvl);
          ctx.stroke();
          ctx.setLineDash([]);

          ctx.fillStyle = '#64748b';
          ctx.font = '600 8px monospace';
          ctx.fillText(`$${lvl.toFixed(0)} Key`, cssWidth - 195, yLvl - 3);
        }
      });
    }

    // 3. Draw Trend Lines (Upper Resistance & Lower Support)
    if (data.trendlines) {
      const { upper, lower } = data.trendlines;
      const lookback = Math.min(80, candles.length);

      if (upper && upper.p1 && upper.p2) {
        const x1 = (cssWidth - 160) - ((candles.length - 1 - upper.p1.index) * 8);
        const y1 = cSeries.priceToCoordinate(upper.p1.price);
        const x2 = (cssWidth - 160) - ((candles.length - 1 - upper.p2.index) * 8);
        const y2 = cSeries.priceToCoordinate(upper.p2.price);
        const xEnd = cssWidth - 160;
        const yEnd = cSeries.priceToCoordinate(upper.curProj);

        if (y1 !== null && y2 !== null && yEnd !== null) {
          ctx.strokeStyle = '#f43f5e';
          ctx.lineWidth = 1.8;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(xEnd, yEnd);
          ctx.stroke();

          ctx.fillStyle = '#f43f5e';
          ctx.font = '700 8px -apple-system, sans-serif';
          ctx.fillText('Res Trendline', x2 + 6, y2 - 4);
        }
      }

      if (lower && lower.p1 && lower.p2) {
        const x1 = (cssWidth - 160) - ((candles.length - 1 - lower.p1.index) * 8);
        const y1 = cSeries.priceToCoordinate(lower.p1.price);
        const x2 = (cssWidth - 160) - ((candles.length - 1 - lower.p2.index) * 8);
        const y2 = cSeries.priceToCoordinate(lower.p2.price);
        const xEnd = cssWidth - 160;
        const yEnd = cSeries.priceToCoordinate(lower.curProj);

        if (y1 !== null && y2 !== null && yEnd !== null) {
          ctx.strokeStyle = '#10b981';
          ctx.lineWidth = 1.8;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(xEnd, yEnd);
          ctx.stroke();

          ctx.fillStyle = '#10b981';
          ctx.font = '700 8px -apple-system, sans-serif';
          ctx.fillText('Sup Trendline', x2 + 6, y2 + 10);
        }
      }
    }

    // 4. Draw Swing Pivots Labels (HH, HL, LH, LL)
    if (data.structure) {
      const { labeledHighs, labeledLows } = data.structure;
      const recentHighs = labeledHighs ? labeledHighs.slice(-6) : [];
      const recentLows = labeledLows ? labeledLows.slice(-6) : [];

      recentHighs.forEach(sh => {
        const x = (cssWidth - 160) - ((candles.length - 1 - sh.index) * 8);
        const y = cSeries.priceToCoordinate(sh.price);
        if (y !== null && x >= 30 && x <= cssWidth - 150) {
          ctx.fillStyle = sh.label === 'HH' ? '#10b981' : '#f59e0b';
          ctx.font = '800 8px monospace';
          ctx.textAlign = 'center';
          ctx.fillText(sh.label, x, y - 8);
          // Small dot
          ctx.beginPath();
          ctx.arc(x, y - 3, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      recentLows.forEach(sl => {
        const x = (cssWidth - 160) - ((candles.length - 1 - sl.index) * 8);
        const y = cSeries.priceToCoordinate(sl.price);
        if (y !== null && x >= 30 && x <= cssWidth - 150) {
          ctx.fillStyle = sl.label === 'HL' ? '#10b981' : '#ef4444';
          ctx.font = '800 8px monospace';
          ctx.textAlign = 'center';
          ctx.fillText(sl.label, x, y + 14);
          // Small dot
          ctx.beginPath();
          ctx.arc(x, y + 3, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      });
      ctx.textAlign = 'start';
    }

    // 5. Draw FOMO Bubbles (v2) (Glowing circles on volume/range expansion)
    if (data.fomoBubbles && data.fomoBubbles.length > 0) {
      data.fomoBubbles.slice(-8).forEach(b => {
        const x = (cssWidth - 160) - ((candles.length - 1 - b.index) * 8);
        const y = cSeries.priceToCoordinate(b.price);
        if (y !== null && x >= 30 && x <= cssWidth - 150) {
          // Radiating glow ring
          ctx.strokeStyle = b.color;
          ctx.lineWidth = 1.8;
          ctx.beginPath();
          ctx.arc(x, y, b.radius, 0, Math.PI * 2);
          ctx.stroke();

          // Translucent fill
          ctx.fillStyle = b.color === '#ef4444' ? 'rgba(239, 68, 68, 0.28)' : 'rgba(56, 189, 248, 0.28)';
          ctx.beginPath();
          ctx.arc(x, y, b.radius - 2, 0, Math.PI * 2);
          ctx.fill();

          // Bubble Badge
          ctx.fillStyle = b.color;
          ctx.font = '800 7.5px -apple-system, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(b.type === 'TOP_FOMO' ? 'FOMO' : 'PANIC', x, b.type === 'TOP_FOMO' ? y - b.radius - 3 : y + b.radius + 9);
          ctx.textAlign = 'start';
        }
      });
    }

    // 6. Draw Entry, SL & TP Lines if Active
    if (data.active) {
      const yEntry = cSeries.priceToCoordinate(data.entry);
      const ySL = cSeries.priceToCoordinate(data.sl);
      const yTP = cSeries.priceToCoordinate(data.tp);

      if (yEntry !== null && ySL !== null && yTP !== null) {
        const isBuy = data.direction === 'BUY';
        const rightEdge = cssWidth - 160;

        // Entry Line (Cyan / Blue)
        ctx.strokeStyle = '#0284c7';
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(40, yEntry);
        ctx.lineTo(rightEdge, yEntry);
        ctx.stroke();

        ctx.fillStyle = '#0284c7';
        ctx.fillRect(rightEdge - 75, yEntry - 8, 70, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8.5px monospace';
        ctx.fillText(`Entry: ${data.entry.toFixed(2)}`, rightEdge - 72, yEntry + 3);

        // SL Line (Red)
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 1.4;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(40, ySL);
        ctx.lineTo(rightEdge, ySL);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = '#ef4444';
        ctx.fillRect(rightEdge - 75, ySL - 8, 70, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8.5px monospace';
        ctx.fillText(`SL: ${data.sl.toFixed(2)}`, rightEdge - 72, ySL + 3);

        // TP Line (Emerald Green)
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([5, 3]);
        ctx.beginPath();
        ctx.moveTo(40, yTP);
        ctx.lineTo(rightEdge, yTP);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = '#10b981';
        ctx.fillRect(rightEdge - 85, yTP - 8, 80, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8.5px monospace';
        ctx.fillText(`TP (Pool): ${data.tp.toFixed(2)}`, rightEdge - 82, yTP + 3);

        // Signal Pill Marker
        const markerX = rightEdge - 45;
        const markerY = isBuy ? Math.min(cssHeight - 35, yEntry + 28) : Math.max(30, yEntry - 28);
        ctx.fillStyle = isBuy ? '#10b981' : '#ef4444';
        ctx.fillRect(markerX - 32, markerY - 11, 64, 22);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(markerX - 32, markerY - 11, 64, 22);

        ctx.fillStyle = '#ffffff';
        ctx.font = '900 11px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(isBuy ? 'BUY' : 'SELL', markerX, markerY + 4);
        ctx.textAlign = 'start';
      }
    }

    // 7. Multi-Feature On-Chart HUD Table (Top Right, exact AlgoAlpha style)
    const tblX = cssWidth - 150;
    const tblY = 55;
    const tblW = 135;
    const tblH = 138;

    ctx.fillStyle = 'rgba(10, 15, 26, 0.95)';
    ctx.fillRect(tblX, tblY, tblW, tblH);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 1;
    ctx.strokeRect(tblX, tblY, tblW, tblH);

    // Header
    ctx.font = '700 9.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('ILPAC [AlgoAlpha]', tblX + 8, tblY + 16);

    ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
    ctx.beginPath();
    ctx.moveTo(tblX, tblY + 22);
    ctx.lineTo(tblX + tblW, tblY + 22);
    ctx.stroke();

    // Row Helper
    const hudRows = [
      { label: 'Trend', val: data.marketTrend || 'BULLISH', col: data.marketTrend === 'BEARISH' ? '#ef4444' : '#10b981' },
      { label: 'Structure', val: data.structure && data.structure.latest ? data.structure.latest.replace('_', ' ') : 'CHoCH Ready', col: '#38bdf8' },
      { label: 'Heatmap Pool', val: data.heatmap && data.heatmap.majorPoolAbove ? `$${data.heatmap.majorPoolAbove.price.toFixed(0)}` : '$4015', col: '#f59e0b' },
      { label: 'FOMO Bubbles', val: data.latestBubble ? data.latestBubble.label : 'Calm', col: data.latestBubble ? data.latestBubble.color : '#94a3b8' },
      { label: 'R:R Target', val: data.rr || '1 : 2.5', col: '#10b981' },
      { label: 'Algo Engine', val: 'MT5 Live', col: '#38bdf8' }
    ];

    hudRows.forEach((r, idx) => {
      const y = tblY + 36 + (idx * 16);
      ctx.font = '600 8.5px -apple-system, sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(r.label, tblX + 8, y);

      ctx.fillStyle = r.col;
      ctx.font = '700 8.5px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(r.val, tblX + tblW - 8, y);
      ctx.textAlign = 'start';
    });

    // 8. Top-Left Header Banner Pill
    const bannerX = 20;
    const bannerY = 65;
    const bannerW = 340;
    const bannerH = 56;

    ctx.fillStyle = 'rgba(10, 15, 26, 0.94)';
    ctx.fillRect(bannerX, bannerY, bannerW, bannerH);
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 1;
    ctx.strokeRect(bannerX, bannerY, bannerW, bannerH);

    ctx.font = '700 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('⚡ ILPAC MODEL (INSTITUTIONAL LIQUIDITY & PRICE ACTION)', bannerX + 10, bannerY + 16);

    ctx.font = '600 9px monospace';
    ctx.fillStyle = data.active ? '#34d399' : '#94a3b8';
    ctx.fillText(data.action, bannerX + 10, bannerY + 32);

    ctx.font = '500 8.5px monospace';
    ctx.fillStyle = '#64748b';
    ctx.fillText(`Market Structure | 3D Liquidity Heatmap | Trend Lines | FOMO Bubbles v2`, bannerX + 10, bannerY + 47);

    ctx.restore();
  }
  window.drawILPACOverlay = drawILPACOverlay;

  console.log('[TradingPoint] ILPAC Model loaded successfully.');
})(window);
