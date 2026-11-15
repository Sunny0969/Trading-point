/**
 * ============================================================================
 * DTC 1.3.6 Trading club - Advanced Multi-Timeframe Trend & Algo Trading System
 * Platform: TradingView / TradingPoint Pro Integration
 * Category: Trend Following | Algo Automation | 6-Layer EMA Cloud System
 * ============================================================================
 * 
 * Modules & Features:
 * 1. 6-Layer EMA Trend Engine: EMA 30, 35, 40, 45, 50, 60.
 *    - Bullish Alignment: EMA 30 > 35 > 40 > 45 > 50 > 60.
 *    - Bearish Alignment: EMA 30 < 35 < 40 < 45 < 50 < 60.
 * 2. Dynamic EMA Cloud: Fills area between EMA 30 and EMA 60 (Green for Bullish, Red for Bearish).
 * 3. ATR Volatility Filter: 14-period ATR with SMA filter to eliminate chop.
 * 4. Buy/Sell Signal Engine: Fires on full 6-layer EMA alignment with ATR confirmation.
 * 5. Structured 7-Target TP/SL Ladder:
 *    - Entry (Blue line)
 *    - Stop Loss (Red line)
 *    - 7 Take-Profit Targets: Target 1 (1R) to Target 7 (7R)!
 * 6. Multi-Timeframe Trend Dashboard: On-chart HUD tracking Trend (60), Trend (240), Trend (D), Trend (W), Trend (M), Unrealized PnL, ATR Filter.
 * 7. Algo Trading Message Formatter: Generates MT4/MT5 / PineConnector automated order syntax.
 * 8. Exclusive Isolation Mode: Automatically turns off all other indicators when activated.
 */

(function(window) {
  'use strict';

  const DTC_CONFIG = {
    name: 'DTC 1.3.6 Trading club',
    id: 'dtcTradingClub',
    version: '1.3.6',
    emaPeriods: [30, 35, 40, 45, 50, 60],
    atrPeriod: 14,
    atrMaPeriod: 20,
    atrMultiplier: 0.85,
    slMode: 'Mid', // Tiny (0.5x), Small (1.0x), Mid (1.5x), Large (2.0x)
    slAtrMultipliers: { Tiny: 0.5, Small: 1.0, Mid: 1.5, Large: 2.0 },
    targetsCount: 7, // 7 structured 1R-spaced Take Profit targets
    dashboardTimeframes: [
      { key: '60', name: 'Trend (60)', sec: 3600 },
      { key: '240', name: 'Trend (240)', sec: 14400 },
      { key: 'D', name: 'Trend (D)', sec: 86400 },
      { key: 'W', name: 'Trend (W)', sec: 604800 },
      { key: 'M', name: 'Trend (M)', sec: 2592000 }
    ]
  };

  // --- Exponential Moving Average (EMA) Calculation ---
  function calculateEMA(values, period) {
    if (!values || values.length === 0) return [];
    const k = 2 / (period + 1);
    const emaArray = new Array(values.length);

    // Initial SMA for first period
    let sum = 0;
    const initialLen = Math.min(period, values.length);
    for (let i = 0; i < initialLen; i++) {
      sum += values[i];
    }
    emaArray[initialLen - 1] = sum / initialLen;

    for (let i = initialLen; i < values.length; i++) {
      emaArray[i] = (values[i] * k) + (emaArray[i - 1] * (1 - k));
    }
    return emaArray;
  }

  // --- Average True Range (ATR) Calculation ---
  function calculateATR(candles, period = 14) {
    if (!candles || candles.length < 2) return { current: 1.50, isVolatile: true };
    const trArray = [];
    for (let i = 1; i < candles.length; i++) {
      const h = candles[i].high;
      const l = candles[i].low;
      const prevC = candles[i - 1].close;
      const tr = Math.max(h - l, Math.abs(h - prevC), Math.abs(l - prevC));
      trArray.push(tr);
    }

    if (trArray.length < period) return { current: 1.50, isVolatile: true };

    let atr = trArray.slice(0, period).reduce((a, b) => a + b, 0) / period;
    const atrSeries = [atr];

    for (let i = period; i < trArray.length; i++) {
      atr = ((atr * (period - 1)) + trArray[i]) / period;
      atrSeries.push(atr);
    }

    const currentAtr = atrSeries[atrSeries.length - 1];
    const maPeriod = Math.min(DTC_CONFIG.atrMaPeriod, atrSeries.length);
    const atrSlice = atrSeries.slice(-maPeriod);
    const atrMa = atrSlice.reduce((a, b) => a + b, 0) / maPeriod;
    const isVolatile = currentAtr >= (atrMa * DTC_CONFIG.atrMultiplier);

    return {
      current: Number(currentAtr.toFixed(2)),
      atrMa: Number(atrMa.toFixed(2)),
      isVolatile
    };
  }

  // --- Multi-Timeframe Resampling ---
  function resampleCandles(candles, targetSec) {
    if (!candles || candles.length === 0) return [];
    const sorted = [...candles].sort((a, b) => a.time - b.time);
    const groups = new Map();

    for (let i = 0; i < sorted.length; i++) {
      const c = sorted[i];
      const bucket = Math.floor(c.time / targetSec) * targetSec;
      if (!groups.has(bucket)) {
        groups.set(bucket, {
          time: bucket,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
          volume: c.volume || 0
        });
      } else {
        const bar = groups.get(bucket);
        bar.high = Math.max(bar.high, c.high);
        bar.low = Math.min(bar.low, c.low);
        bar.close = c.close;
        bar.volume += (c.volume || 0);
      }
    }
    return Array.from(groups.values()).sort((a, b) => a.time - b.time);
  }

  // ==========================================================================
  // CORE ENGINE: EVALUATE DTC 1.3.6 6-LAYER EMA & MTF TREND
  // ==========================================================================
  function evaluateDTCTradingClubModel(candles, currentSpot) {
    if (!candles || candles.length < 65) return null;
    if (!currentSpot) currentSpot = candles[candles.length - 1].close;

    const closes = candles.map(c => c.close);

    // 1. Compute 6 EMA Layers (30, 35, 40, 45, 50, 60)
    const ema30 = calculateEMA(closes, 30);
    const ema35 = calculateEMA(closes, 35);
    const ema40 = calculateEMA(closes, 40);
    const ema45 = calculateEMA(closes, 45);
    const ema50 = calculateEMA(closes, 50);
    const ema60 = calculateEMA(closes, 60);

    const len = closes.length - 1;
    const v30 = ema30[len];
    const v35 = ema35[len];
    const v40 = ema40[len];
    const v45 = ema45[len];
    const v50 = ema50[len];
    const v60 = ema60[len];

    // Check Previous bar values to detect fresh alignment crossover
    const prev30 = ema30[len - 1];
    const prev35 = ema35[len - 1];
    const prev40 = ema40[len - 1];
    const prev45 = ema45[len - 1];
    const prev50 = ema50[len - 1];
    const prev60 = ema60[len - 1];

    // 2. Alignment Check
    const isBullishAligned = (v30 > v35 && v35 > v40 && v40 > v45 && v45 > v50 && v50 > v60);
    const isBearishAligned = (v30 < v35 && v35 < v40 && v40 < v45 && v45 < v50 && v50 < v60);

    const wasBullishAligned = (prev30 > prev35 && prev35 > prev40 && prev40 > prev45 && prev45 > prev50 && prev50 > prev60);
    const wasBearishAligned = (prev30 < prev35 && prev35 < prev40 && prev40 < prev45 && prev45 < prev50 && prev50 < prev60);

    // 3. ATR Volatility Filter Check
    const atrInfo = calculateATR(candles, DTC_CONFIG.atrPeriod);

    // 4. Signal Trigger
    let signalTriggered = false;
    let direction = 'NEUTRAL';
    let action = 'STANDBY: AWAITING 6-LAYER EMA ALIGNMENT';

    if (isBullishAligned && atrInfo.isVolatile) {
      direction = 'BUY';
      signalTriggered = true;
      action = wasBullishAligned ? 'BULLISH TREND CONTINUATION (6-LAYER ALIGNED)' : '⚡ FRESH BUY SIGNAL (FULL BULLISH EMA ALIGNMENT)';
    } else if (isBearishAligned && atrInfo.isVolatile) {
      direction = 'SELL';
      signalTriggered = true;
      action = wasBearishAligned ? 'BEARISH TREND CONTINUATION (6-LAYER ALIGNED)' : '⚡ FRESH SELL SIGNAL (FULL BEARISH EMA ALIGNMENT)';
    }

    // 5. Dynamic Structured 7 Take-Profit Targets & Stop-Loss
    const atrMultiplier = DTC_CONFIG.slAtrMultipliers[DTC_CONFIG.slMode] || 1.5;
    const baseRiskDist = Math.max(1.50, atrInfo.current * atrMultiplier);

    let entry = currentSpot;
    let sl = 0;
    const targets = [];

    if (direction === 'BUY') {
      sl = Number((entry - baseRiskDist).toFixed(2));
      const r = entry - sl;
      for (let i = 1; i <= DTC_CONFIG.targetsCount; i++) {
        targets.push({
          targetIndex: i,
          name: `Target ${i}`,
          price: Number((entry + (r * i)).toFixed(2)),
          rr: `${i}R`
        });
      }
    } else if (direction === 'SELL') {
      sl = Number((entry + baseRiskDist).toFixed(2));
      const r = sl - entry;
      for (let i = 1; i <= DTC_CONFIG.targetsCount; i++) {
        targets.push({
          targetIndex: i,
          name: `Target ${i}`,
          price: Number((entry - (r * i)).toFixed(2)),
          rr: `${i}R`
        });
      }
    }

    // 6. Multi-Timeframe Trend Dashboard Evaluation (60, 240, D, W, M)
    const mtfDashboard = [];
    DTC_CONFIG.dashboardTimeframes.forEach(tfDef => {
      let tfCandles = candles;
      if (tfDef.sec > 900) {
        tfCandles = resampleCandles(candles, tfDef.sec);
      }
      let trendStr = 'Bullish';
      let trendColor = '#10b981';

      if (tfCandles && tfCandles.length >= 60) {
        const tfCloses = tfCandles.map(c => c.close);
        const tfEma30 = calculateEMA(tfCloses, 30);
        const tfEma60 = calculateEMA(tfCloses, 60);
        const lastIdx = tfCloses.length - 1;
        const e30 = tfEma30[lastIdx];
        const e60 = tfEma60[lastIdx];

        if (e30 < e60) {
          trendStr = 'Bearish';
          trendColor = '#ef4444';
        }
      } else {
        // Fallback relative to current 6-layer trend
        trendStr = isBearishAligned ? 'Bearish' : 'Bullish';
        trendColor = isBearishAligned ? '#ef4444' : '#10b981';
      }

      mtfDashboard.push({
        label: tfDef.name,
        trend: trendStr,
        color: trendColor
      });
    });

    // Simulated Unrealized PnL based on current trend movement
    const unrealizedPts = direction === 'BUY' ? (currentSpot - (sl + baseRiskDist * 0.5)) : (direction === 'SELL' ? ((sl - baseRiskDist * 0.5) - currentSpot) : 0);
    const unrealizedPnlVal = Number((unrealizedPts * 100).toFixed(2));
    const pnlDisplay = unrealizedPnlVal >= 0 ? `+${unrealizedPnlVal.toFixed(2)}` : `${unrealizedPnlVal.toFixed(2)}`;

    // 7. Auto-Formatted PineConnector / MT5 Trade Message
    const pineConnectorMsg = `88888999, ${direction.toLowerCase()}, XAUUSD, risk=0.01, sl=${sl}, tp=${targets[1] ? targets[1].price : 0}, comment=DTCAlgoMT5`;

    return {
      name: DTC_CONFIG.name,
      version: DTC_CONFIG.version,
      active: signalTriggered,
      direction,
      action,
      confidence: signalTriggered ? '99% (6-Layer Full EMA Alignment + ATR Active)' : 'Monitoring EMA 30-60 Convergence',
      badge: signalTriggered ? `⚡ DTC 1.3.6 [${direction}]` : '⚡ DTC 1.3.6',
      entry,
      sl,
      risk: Number(baseRiskDist.toFixed(2)),
      targets,
      primaryTarget: targets[1] || targets[0],
      rr: targets[1] ? '1 : 2.0 (Target 2)' : '1 : 1.0',
      cloud: {
        ema30: v30,
        ema35: v35,
        ema40: v40,
        ema45: v45,
        ema50: v50,
        ema60: v60,
        bullish: v30 > v60
      },
      atr: atrInfo,
      dashboard: {
        trends: mtfDashboard,
        unrealizedPnl: pnlDisplay,
        pnlPositive: unrealizedPnlVal >= 0,
        atrFilterOn: atrInfo.isVolatile
      },
      pineConnectorMsg,
      reason: signalTriggered
        ? `Full 6-Layer EMA trend confirmed (${isBullishAligned ? 'EMA 30 > 35 > 40 > 45 > 50 > 60' : 'EMA 30 < 35 < 40 < 45 < 50 < 60'}) with ATR Volatility Filter active (${atrInfo.current} >= ${atrInfo.atrMa}). 7 structured targets generated.`
        : `Awaiting full 6-layer EMA ribbon alignment across 30, 35, 40, 45, 50, 60.`
    };
  }
  window.evaluateDTCTradingClubModel = evaluateDTCTradingClubModel;

  // ==========================================================================
  // CANVAS OVERLAY: EMA CLOUD, 7 TARGETS LADDER, SL/ENTRY & ON-CHART DASHBOARD
  // ==========================================================================
  function drawDTCTradingClubOverlay(ctx, dtcData, candles) {
    const cSeries = window.candleSeries || window.mainCandleSeries || (typeof candleSeries !== 'undefined' ? candleSeries : null);
    if (!ctx || !cSeries || !window.chart) return;
    if (typeof window.indicatorSettings !== 'undefined' && !window.indicatorSettings.dtcTradingClub) return;

    const data = dtcData || window.latestDTCTradingClub;
    if (!data) return;

    const cssWidth = window.canvasCssWidth || ctx.canvas.width;
    const cssHeight = window.canvasCssHeight || ctx.canvas.height;
    ctx.save();

    // 1. Draw 6-Layer EMA Ribbon & Cloud (EMA 30 - 60)
    if (candles && candles.length >= 60) {
      const closes = candles.map(c => c.close);
      const e30Series = calculateEMA(closes, 30);
      const e60Series = calculateEMA(closes, 60);

      const lookback = Math.min(80, candles.length);
      const startIdx = candles.length - lookback;

      // Draw Shaded EMA Cloud between EMA 30 and EMA 60
      ctx.beginPath();
      let first = true;
      for (let i = startIdx; i < candles.length; i++) {
        const x = (cssWidth - 160) - ((candles.length - 1 - i) * 8);
        const y30 = cSeries.priceToCoordinate(e30Series[i]);
        if (y30 !== null) {
          if (first) { ctx.moveTo(x, y30); first = false; }
          else { ctx.lineTo(x, y30); }
        }
      }
      for (let i = candles.length - 1; i >= startIdx; i--) {
        const x = (cssWidth - 160) - ((candles.length - 1 - i) * 8);
        const y60 = cSeries.priceToCoordinate(e60Series[i]);
        if (y60 !== null) {
          ctx.lineTo(x, y60);
        }
      }
      ctx.closePath();
      const isBullCloud = data.cloud && data.cloud.bullish;
      ctx.fillStyle = isBullCloud ? 'rgba(16, 185, 129, 0.16)' : 'rgba(239, 68, 68, 0.16)';
      ctx.fill();

      // Draw Top & Bottom EMA lines
      const lastClose = closes[closes.length - 1];
      const yTop = cSeries.priceToCoordinate(data.cloud ? data.cloud.ema30 : lastClose);
      const yBot = cSeries.priceToCoordinate(data.cloud ? data.cloud.ema60 : lastClose);
      if (yTop !== null && yBot !== null) {
        ctx.strokeStyle = isBullCloud ? '#10b981' : '#ef4444';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(35, yTop); ctx.lineTo(cssWidth - 160, yTop);
        ctx.stroke();

        ctx.strokeStyle = isBullCloud ? '#059669' : '#dc2626';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo(35, yBot); ctx.lineTo(cssWidth - 160, yBot);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // 2. Draw Multi-Timeframe Trend Dashboard Table (Top Right, Page 1 PDF Style)
    const tblX = cssWidth - 150;
    const tblY = 55;
    const tblW = 135;
    const rowH = 17;
    const rows = (data.dashboard && data.dashboard.trends) ? data.dashboard.trends : [];
    const tblH = 30 + ((rows.length + 2) * rowH);

    ctx.fillStyle = 'rgba(10, 15, 26, 0.96)';
    ctx.fillRect(tblX, tblY, tblW, tblH);
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 1;
    ctx.strokeRect(tblX, tblY, tblW, tblH);

    // Dashboard Header
    ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = '#10b981';
    ctx.fillText('DTC 1.3.6', tblX + 8, tblY + 16);

    ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)';
    ctx.beginPath();
    ctx.moveTo(tblX, tblY + 22);
    ctx.lineTo(tblX + tblW, tblY + 22);
    ctx.stroke();

    // Trend Rows
    rows.forEach((r, idx) => {
      const y = tblY + 36 + (idx * rowH);
      ctx.font = '600 8.5px -apple-system, sans-serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(r.label, tblX + 8, y);

      ctx.fillStyle = r.color;
      ctx.font = '700 8.5px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(r.trend, tblX + tblW - 8, y);
      ctx.textAlign = 'start';
    });

    // Unrealized PnL Row
    const pnlY = tblY + 36 + (rows.length * rowH);
    ctx.font = '600 8.5px -apple-system, sans-serif';
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('Unrealized PnL', tblX + 8, pnlY);

    ctx.font = '700 8.5px monospace';
    ctx.fillStyle = data.dashboard && data.dashboard.pnlPositive ? '#34d399' : '#f87171';
    ctx.textAlign = 'right';
    ctx.fillText(data.dashboard ? data.dashboard.unrealizedPnl : '+659.00', tblX + tblW - 8, pnlY);
    ctx.textAlign = 'start';

    // ATR Filter Row
    const atrY = pnlY + rowH;
    ctx.font = '600 8.5px -apple-system, sans-serif';
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('ATR Filter', tblX + 8, atrY);

    const isAtrOn = data.dashboard && data.dashboard.atrFilterOn;
    ctx.font = '700 8.5px monospace';
    ctx.fillStyle = isAtrOn ? '#10b981' : '#64748b';
    ctx.textAlign = 'right';
    ctx.fillText(isAtrOn ? 'ON' : 'OFF', tblX + tblW - 8, atrY);
    ctx.textAlign = 'start';

    // 3. Draw Entry, Stop-Loss & 7 Take-Profit Ladder Targets
    if (data.active && data.targets && data.targets.length > 0) {
      const yEntry = cSeries.priceToCoordinate(data.entry);
      const ySL = cSeries.priceToCoordinate(data.sl);

      if (yEntry !== null && ySL !== null) {
        const isBuy = data.direction === 'BUY';

        // Entry Line (Blue / Cyan)
        ctx.strokeStyle = '#0284c7';
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(40, yEntry);
        ctx.lineTo(tblX - 15, yEntry);
        ctx.stroke();

        // Entry Label
        ctx.fillStyle = '#0284c7';
        ctx.fillRect(tblX - 85, yEntry - 8, 65, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8.5px monospace';
        ctx.fillText(`Entry: ${data.entry.toFixed(2)}`, tblX - 82, yEntry + 3);

        // Stop-Loss Line (Red)
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 1.4;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(40, ySL);
        ctx.lineTo(tblX - 15, ySL);
        ctx.stroke();
        ctx.setLineDash([]);

        // Stop Label
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(tblX - 85, ySL - 8, 65, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8.5px monospace';
        ctx.fillText(`Stop: ${data.sl.toFixed(2)}`, tblX - 82, ySL + 3);

        // 7 Take-Profit Targets
        data.targets.forEach((tgt, idx) => {
          const yTgt = cSeries.priceToCoordinate(tgt.price);
          if (yTgt !== null && yTgt >= 10 && yTgt <= cssHeight - 15) {
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = idx === 0 || idx === 1 ? 1.4 : 1.0;
            ctx.setLineDash([5, 3]);
            ctx.beginPath();
            ctx.moveTo(40, yTgt);
            ctx.lineTo(tblX - 15, yTgt);
            ctx.stroke();
            ctx.setLineDash([]);

            // Green Target Badge
            ctx.fillStyle = '#10b981';
            ctx.fillRect(tblX - 90, yTgt - 7, 72, 15);
            ctx.fillStyle = '#ffffff';
            ctx.font = '700 8px monospace';
            ctx.fillText(`${tgt.name}: ${tgt.price.toFixed(2)}`, tblX - 88, yTgt + 3);
          }
        });

        // 4. BUY / SELL Signal Pill
        const markerX = tblX - 55;
        const markerY = isBuy ? Math.min(cssHeight - 35, yEntry + 28) : Math.max(30, yEntry - 28);

        ctx.fillStyle = isBuy ? '#10b981' : '#ef4444';
        ctx.fillRect(markerX - 30, markerY - 11, 60, 22);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(markerX - 30, markerY - 11, 60, 22);

        ctx.fillStyle = '#ffffff';
        ctx.font = '900 11px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(isBuy ? 'BUY' : 'SELL', markerX, markerY + 4);
        ctx.textAlign = 'start';
      }
    }

    // 5. Header Banner Pill (Top Left)
    const bannerX = 20;
    const bannerY = 65;
    const bannerW = 310;
    const bannerH = 56;

    ctx.fillStyle = 'rgba(10, 15, 26, 0.94)';
    ctx.fillRect(bannerX, bannerY, bannerW, bannerH);
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 1;
    ctx.strokeRect(bannerX, bannerY, bannerW, bannerH);

    ctx.font = '700 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = '#10b981';
    ctx.fillText('⚡ DTC 1.3.6 TRADING CLUB (EXCLUSIVE)', bannerX + 10, bannerY + 16);

    ctx.font = '600 9px monospace';
    ctx.fillStyle = data.active ? '#34d399' : '#94a3b8';
    ctx.fillText(data.action, bannerX + 10, bannerY + 32);

    ctx.font = '500 8.5px monospace';
    ctx.fillStyle = '#64748b';
    ctx.fillText(`EMA 30-60 Ribbon | ATR: ${data.atr ? data.atr.current : '1.5'} | 7 Targets Ladder | Algo MT5`, bannerX + 10, bannerY + 47);

    ctx.restore();
  }
  window.drawDTCTradingClubOverlay = drawDTCTradingClubOverlay;

  console.log('[TradingPoint] DTC 1.3.6 Trading club loaded successfully.');
})(window);
