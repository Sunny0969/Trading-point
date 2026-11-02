import sys

def main():
    # Read fresh from gold_dashboard.html
    # First, let's restore to clean base or reapply correctly
    with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Refine telemetry candle resolution
    old_telemetry = '''// Dedicated: SMC M5 PULLBACK SNIPER (BOS + OB + 0.618 FIBO + IFVG TP) TELEMETRY
      let m5Candles = candles;
      if (window.mtfCandleStore && window.mtfCandleStore['5m'] && window.mtfCandleStore['5m'].length >= 25) {
        m5Candles = window.mtfCandleStore['5m'];
      } else if (typeof resampleCandles === 'function' && candles && candles.length >= 30) {
        const curSec = (typeof currentTf !== 'undefined' && currentTf === '1m') ? 60 : 900;
        m5Candles = resampleCandles(candles, curSec, 300);
      }
      const obFiboResult = evaluateSMC_OB_FiboSetup(m5Candles);
      window.latestSMC_OB_Fibo = obFiboResult;

      if (obFiboResult) {
        if (obFiboResult.isTriggered) {
          modularEngineState.indicators.OB_FIBO = {
            status: '0.618 RETEST CONFIRMED',
            direction: 'SELL / SHORT',
            entry: '$' + Number(obFiboResult.entry).toFixed(2),
            sl: '$' + Number(obFiboResult.sl).toFixed(2),
            tp: '$' + Number(obFiboResult.tp).toFixed(2),
            rr: obFiboResult.rr || '1 : 3.8',
            reason: obFiboResult.reason || 'M5 BOS confirmed. Price completed 0.618 Fibonacci pullback into Bearish Order Block. Rejection confirms institutional selling pressure.'
          };
        } else {
          modularEngineState.indicators.OB_FIBO = {
            status: 'WAITING PULLBACK',
            direction: 'SELL',
            entry: '$' + Number(obFiboResult.entry || obFiboResult.fiboLevel).toFixed(2),
            sl: '$' + Number(obFiboResult.sl || (parseFloat(obFiboResult.obLevel) + 1.20)).toFixed(2),
            tp: '$' + Number(obFiboResult.tp || (parseFloat(obFiboResult.entry) - 8.0)).toFixed(2),
            rr: obFiboResult.rr || '1 : 3.8',
            reason: obFiboResult.reason || `BOS detected at $${obFiboResult.swingLow}. Waiting for retracement pullback to 0.618 Fibo ($${obFiboResult.fiboLevel}). Do not chase early.`
          };
        }
      } else {
        modularEngineState.indicators.OB_FIBO = {
          status: 'STANDBY',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Awaiting M5 Imbalance & Break of Structure (BOS).'
        };
      }'''

    new_telemetry = '''// Dedicated: SMC M5 PULLBACK SNIPER (BOS + OB + 0.618 FIBO + IFVG TP) TELEMETRY
      let m5Candles = candles;
      if (window.mtfCandleStore && window.mtfCandleStore['5m'] && window.mtfCandleStore['5m'].length >= 30) {
        m5Candles = window.mtfCandleStore['5m'];
      } else if (typeof currentTf !== 'undefined' && currentTf === '5m' && candles && candles.length >= 30) {
        m5Candles = candles;
      } else if (typeof resampleCandles === 'function' && candles && candles.length >= 60 && typeof currentTf !== 'undefined' && currentTf !== '5m') {
        const curSec = (currentTf === '1m') ? 60 : 900;
        const resampled = resampleCandles(candles, curSec, 300);
        if (resampled && resampled.length >= 30) m5Candles = resampled;
      }
      if (!m5Candles || m5Candles.length < 30) {
        m5Candles = candles;
      }
      const obFiboResult = evaluateSMC_OB_FiboSetup(m5Candles);
      window.latestSMC_OB_Fibo = obFiboResult;

      if (obFiboResult) {
        if (obFiboResult.isTriggered) {
          modularEngineState.indicators.OB_FIBO = {
            status: '0.618 RETEST CONFIRMED',
            stateBadge: '0.618 RETEST CONFIRMED',
            direction: 'SELL / SHORT',
            entry: '$' + Number(obFiboResult.entry).toFixed(2),
            sl: '$' + Number(obFiboResult.sl).toFixed(2),
            tp: '$' + Number(obFiboResult.tp).toFixed(2),
            rr: obFiboResult.rr || '1 : 3.8',
            reason: obFiboResult.reason || 'M5 BOS confirmed. Price completed 0.618 Fibonacci pullback into Bearish Order Block. Rejection confirms institutional selling pressure.'
          };
        } else {
          modularEngineState.indicators.OB_FIBO = {
            status: 'WAITING PULLBACK',
            stateBadge: 'WAITING PULLBACK',
            direction: 'STANDBY',
            entry: '$' + Number(obFiboResult.entry || obFiboResult.fiboLevel).toFixed(2),
            sl: '$' + Number(obFiboResult.sl || (parseFloat(obFiboResult.obLevel) + 1.20)).toFixed(2),
            tp: '$' + Number(obFiboResult.tp || (parseFloat(obFiboResult.entry) - 8.0)).toFixed(2),
            rr: obFiboResult.rr || '1 : 3.8',
            reason: obFiboResult.reason || `BOS detected at $${obFiboResult.swingLow}. Waiting for retracement pullback to 0.618 Fibo ($${obFiboResult.fiboLevel}). Do not chase early.`
          };
        }
      } else {
        modularEngineState.indicators.OB_FIBO = {
          status: 'STANDBY',
          stateBadge: 'STANDBY',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Awaiting M5 Imbalance & Break of Structure (BOS).'
        };
      }'''

    if old_telemetry in html:
        html = html.replace(old_telemetry, new_telemetry, 1)
        print("Updated telemetry candle resolution and stateBadge successfully.")
    else:
        print("WARNING: old_telemetry not matched exactly.")

    # Refine State Badge in renderModularTelemetryUI header
    old_badge_span = '<span style="font-size: 10px; padding: 2px 7px; border-radius: 10px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeBorder}; font-family: monospace; font-weight: 700;">\n              ${activeData.direction}\n            </span>'
    alt_badge_span = '<span style="font-size: 10px; padding: 2px 7px; border-radius: 10px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeBorder}; font-family: monospace; font-weight: 700;">\r\n              ${activeData.direction}\r\n            </span>'
    new_badge_span = '<span style="font-size: 10px; padding: 2px 7px; border-radius: 10px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeBorder}; font-family: monospace; font-weight: 700;">\n              ${activeTab === \'OB_FIBO\' && activeData.stateBadge ? activeData.stateBadge : activeData.direction}\n            </span>'
    
    if old_badge_span in html:
        html = html.replace(old_badge_span, new_badge_span, 1)
        print("Updated card badge span.")
    elif alt_badge_span in html:
        html = html.replace(alt_badge_span, new_badge_span, 1)
        print("Updated alt card badge span.")
    else:
        print("WARNING: badge span not found for replacement.")

    for fname in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved {fname} ({len(html)} bytes)")

    return True

if __name__ == '__main__':
    main()
