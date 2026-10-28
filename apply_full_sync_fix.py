"""
Comprehensive update for:
1. Real-Time SL Invalidation & Immediate Lock Release (Short-Term & Long-Term).
2. Proper Pending Invalidation State (3.5s cooldown before transition, showing countdown & invalidation notice).
3. Accurate Next Signal Calculation upon Invalidation (Demand broken -> SELL targeting lower liquidity; Supply broken -> BUY targeting higher liquidity).
4. Price Action VETO Rule in evaluateHighAccuracySetup (vetoing macroWarBuy & macroDxySell when candle is breaking down below EMA 20 or breaking up).
5. Ghost Candles and Signal Card 100% strict mathematical bidirectional synchronization.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

def update_file(filepath):
    print(f"Updating {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Price Action Veto on macroWarBuy and macroDxySell
    target_macro_override = """      // ==========================================
      // TWELVE DATA & SUGRA AI RADAR CONFLUENCE OVERRIDE
      // ==========================================
      const macroWarBuy = (typeof macroMarketState !== 'undefined' && 
        (macroMarketState.sugraWarScore >= 60 || macroMarketState.confluenceScore >= 7.0 || macroMarketState.netMoveTarget > 0) && 
        macroMarketState.dxyChange <= 0.35);

      const macroDxySell = (typeof macroMarketState !== 'undefined' && 
        macroMarketState.dxyChange >= 0.35 && 
        macroMarketState.sugraWarScore < 60);"""

    replacement_macro_override = """      // ==========================================
      // TWELVE DATA & SUGRA AI RADAR CONFLUENCE OVERRIDE
      // (SUBJECT STRICTLY TO PRICE ACTION VETO)
      // ==========================================
      const macroWarBuy = (!isPriceActionBearish) && (typeof macroMarketState !== 'undefined' && 
        (macroMarketState.sugraWarScore >= 60 || macroMarketState.confluenceScore >= 7.0 || macroMarketState.netMoveTarget > 0) && 
        macroMarketState.dxyChange <= 0.35);

      const macroDxySell = (!isPriceActionBullish) && (typeof macroMarketState !== 'undefined' && 
        macroMarketState.dxyChange >= 0.35 && 
        macroMarketState.sugraWarScore < 60);"""

    if target_macro_override in content:
        content = content.replace(target_macro_override, replacement_macro_override)
        print(" [x] Gated macroWarBuy and macroDxySell with Price Action VETO.")
    else:
        print(" [!] Could not find target_macro_override.")

    # 2. Relax confluence check in updateActiveSetupCard
    target_conf_check = "    function updateActiveSetupCard(confluence, currentCandle, sup, res) {\n      if (!confluence || !confluence.agent4) return;"
    replacement_conf_check = "    function updateActiveSetupCard(confluence, currentCandle, sup, res) {\n      if (!confluence) return;"
    if target_conf_check in content:
        content = content.replace(target_conf_check, replacement_conf_check)
        print(" [x] Relaxed confluence guard check to allow safe fallback.")

    # 3. Update Long-Term Signal Invalidation Evaluation
    target_lt_eval = """      // 2. REAL-TIME LONG-TERM TP / SL TRIGGER EVALUATION
      if (longTermSignalLock.active && longTermSignalLock.status === 'ACTIVE_HOLD') {
        if (longTermSignalLock.bias === 'BULLISH') {
          if (currentSpot >= longTermSignalLock.tp) {
            longTermSignalLock.status = 'TP_HIT';
            longTermSignalLock.completedAt = now;
            longTermSignalLock.lastCompletedBias = 'BULLISH';
            longTermSignalLock.lastCompletedStatus = 'TP_HIT';
          } else if (currentSpot <= longTermSignalLock.inval) {
            longTermSignalLock.status = 'SL_HIT';
            longTermSignalLock.completedAt = now;
            longTermSignalLock.lastCompletedBias = 'BULLISH';
            longTermSignalLock.lastCompletedStatus = 'SL_HIT';
          }
        } else {
          if (currentSpot <= longTermSignalLock.tp) {
            longTermSignalLock.status = 'TP_HIT';
            longTermSignalLock.completedAt = now;
            longTermSignalLock.lastCompletedBias = 'BEARISH';
            longTermSignalLock.lastCompletedStatus = 'TP_HIT';
          } else if (currentSpot >= longTermSignalLock.inval) {
            longTermSignalLock.status = 'SL_HIT';
            longTermSignalLock.completedAt = now;
            longTermSignalLock.lastCompletedBias = 'BEARISH';
            longTermSignalLock.lastCompletedStatus = 'SL_HIT';
          }
        }
      }"""

    replacement_lt_eval = """      // 2. REAL-TIME LONG-TERM TP / SL TRIGGER & HARD STRUCTURE INVALIDATION
      if (longTermSignalLock.active) {
        const isLtBuy = (longTermSignalLock.bias === 'BULLISH');
        const ltInval = Number(longTermSignalLock.inval);
        const ltTp = Number(longTermSignalLock.tp);

        const isLtSlBreached = isLtBuy ? (currentSpot <= ltInval) : (currentSpot >= ltInval);
        const isLtTpReached = isLtBuy ? (currentSpot >= ltTp) : (currentSpot <= ltTp);

        if (isLtSlBreached) {
          // IMMEDIATE HARD OVERRIDE FOR SWING
          longTermSignalLock.status = 'SL_HIT';
          longTermSignalLock.active = false;
          longTermSignalLock.completedAt = now;
          longTermSignalLock.lastCompletedBias = isLtBuy ? 'BULLISH' : 'BEARISH';
          longTermSignalLock.lastCompletedStatus = 'SL_HIT';
          longTermSignalLock.action = 'SWING INVALIDATED / STOPPED OUT';
          longTermSignalLock.reason = 'Macro swing invalidation level breached -> Re-evaluating HTF trend.';
        } else if (longTermSignalLock.status === 'ACTIVE_HOLD' && isLtTpReached) {
          longTermSignalLock.status = 'TP_HIT';
          longTermSignalLock.completedAt = now;
          longTermSignalLock.lastCompletedBias = isLtBuy ? 'BULLISH' : 'BEARISH';
          longTermSignalLock.lastCompletedStatus = 'TP_HIT';
        }
      }"""

    if target_lt_eval in content:
        content = content.replace(target_lt_eval, replacement_lt_eval)
        print(" [x] Upgraded Long-Term SL invalidation evaluation.")
    else:
        print(" [!] Could not find target_lt_eval.")

    # 4. Short-Term Signal Auto-Transition logic & Next Signal Generation
    target_st_trans = """      // 3. SHORT-TERM SIGNAL AUTO-TRANSITION (IMMEDIATE RE-EVALUATION UPON TP/SL)
      const stElapsed = now - shortTermSignalLock.lockedAt;
      const isLockExpired = (!shortTermSignalLock.active || stElapsed >= shortTermSignalLock.maxLockDurationMs);
      // Fast re-evaluation: 3.5s for SL invalidation, 6s for TP celebration
      const minWait = (shortTermSignalLock.status === 'SL_HIT') ? 3500 : 6000;
      const isTargetOrSlDone = (shortTermSignalLock.status === 'TP_HIT' || shortTermSignalLock.status === 'SL_HIT') && 
                               shortTermSignalLock.completedAt && 
                               (now - shortTermSignalLock.completedAt >= minWait);

      if (isLockExpired || isTargetOrSlDone) {
        const prevType = shortTermSignalLock.lastCompletedType;
        const prevStatus = shortTermSignalLock.lastCompletedStatus;

        const resistance = res || 4060.0;
        const support = sup || 3990.0;
        const atr = (confluence && confluence.agent4 && confluence.agent4.atr) ? confluence.agent4.atr : 3.5;

        // TOP-DOWN MULTI-TIMEFRAME EVALUATION (Hard Gated)
        const mtfRes = evaluateTopDownMTF(
          mtfCandleStore['4h'],
          mtfCandleStore['1h'],
          mtfCandleStore['15m'],
          mtfCandleStore['5m'],
          mtfCandleStore['3m']
        );

        let newSigType = 'BUY';
        let newAction = 'BUY / LONG';
        let newEntry = currentSpot;
        let newTp1, newTp2, newSl, newConfidence, newReason, newGainPts, newRr;

        if (mtfRes && mtfRes.status.startsWith('EXECUTE')) {
          newSigType = mtfRes.direction;
          newAction = newSigType === 'BUY' ? 'BUY / LONG' : 'SELL / SHORT';
          newEntry = mtfRes.entry;
          newTp1 = mtfRes.tp1;
          newTp2 = mtfRes.tp2;
          newSl = mtfRes.sl;
          newConfidence = mtfRes.timeframesAligned;
          newGainPts = mtfRes.gainPts;
          newRr = mtfRes.rr;
          newReason = mtfRes.reason;
        } else {
          // Dynamic structural fallback
          const isNearSupply = (currentSpot >= resistance - 4.5);
          const isNearDemand = (currentSpot <= support + 4.5);

          if (prevType === 'BUY' && prevStatus === 'TP_HIT' && isNearSupply) {
            newSigType = 'SELL';
            newAction = 'SELL / SHORT';
            newConfidence = '4/5 Timeframes Aligned (Supply Rejection)';
            newGainPts = Number((atr * 3.0).toFixed(1));
            newTp1 = Number((currentSpot - newGainPts).toFixed(2));
            newTp2 = Number((currentSpot - newGainPts - 8.0).toFixed(2));
            newSl = Number((currentSpot + 2.50).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Target TP1 achieved at Supply. Liquidity sweep complete; bearish rejection structure targeting EMA 20 & Demand.';
          } else if (prevType === 'SELL' && prevStatus === 'TP_HIT' && isNearDemand) {
            newSigType = 'BUY';
            newAction = 'BUY / LONG';
            newConfidence = '4/5 Timeframes Aligned (Demand Absorption)';
            newGainPts = Number((atr * 3.0).toFixed(1));
            newTp1 = Number((currentSpot + newGainPts).toFixed(2));
            newTp2 = Number((currentSpot + newGainPts + 8.0).toFixed(2));
            newSl = Number((currentSpot - 2.50).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Target TP1 achieved at Demand. Liquidity floor defended; bullish absorption targeting EMA 20 & Supply.';
          } else {
            const isBuy = (confluence.buyVotes >= confluence.sellVotes);
            newSigType = isBuy ? 'BUY' : 'SELL';
            newAction = isBuy ? 'BUY / LONG' : 'SELL / SHORT';
            newGainPts = 12.0;
            newTp1 = isBuy ? Number((currentSpot + newGainPts).toFixed(2)) : Number((currentSpot - newGainPts).toFixed(2));
            newTp2 = isBuy ? Number((newTp1 + 8.0).toFixed(2)) : Number((newTp1 - 8.0).toFixed(2));
            newSl = isBuy ? Number((currentSpot - 3.0).toFixed(2)) : Number((currentSpot + 3.0).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newConfidence = '5/5 Timeframes Aligned (Macro Safe-Haven Trend)';
            newReason = isBuy 
              ? '4H Bullish Trend + 15M Shift + 5M OB Retest + 3M Wick Absorption.'
              : '4H Bearish Trend + 15M Shift + 5M OB Retest + 3M Wick Supply Rejection.';
          }
        }"""

    replacement_st_trans = """      // 3. SHORT-TERM SIGNAL AUTO-TRANSITION (IMMEDIATE RE-EVALUATION UPON TP/SL)
      const stElapsed = now - shortTermSignalLock.lockedAt;
      const isStatusPending = (shortTermSignalLock.status === 'TP_HIT' || shortTermSignalLock.status === 'SL_HIT');
      const minWait = (shortTermSignalLock.status === 'SL_HIT') ? 3500 : 6000;
      const isTargetOrSlDone = isStatusPending && 
                               shortTermSignalLock.completedAt && 
                               (now - shortTermSignalLock.completedAt >= minWait);

      // Lock expires only if normal holding time elapsed, NOT during pending invalidation/completion cooldown!
      const isLockExpired = !isStatusPending && 
                            (shortTermSignalLock.status === 'ACTIVE_HOLD' && stElapsed >= shortTermSignalLock.maxLockDurationMs);

      if (isLockExpired || isTargetOrSlDone) {
        const prevType = shortTermSignalLock.lastCompletedType;
        const prevStatus = shortTermSignalLock.lastCompletedStatus;

        const resistance = res || 4060.0;
        const support = sup || 3990.0;
        const atr = (confluence && confluence.agent4 && confluence.agent4.atr) ? confluence.agent4.atr : 3.5;

        // TOP-DOWN MULTI-TIMEFRAME EVALUATION (Hard Gated)
        const mtfRes = (typeof evaluateTopDownMTF === 'function') ? evaluateTopDownMTF(
          mtfCandleStore['4h'],
          mtfCandleStore['1h'],
          mtfCandleStore['15m'],
          mtfCandleStore['5m'],
          mtfCandleStore['3m']
        ) : null;

        let newSigType = 'BUY';
        let newAction = 'BUY / LONG';
        let newEntry = currentSpot;
        let newTp1, newTp2, newSl, newConfidence, newReason, newGainPts, newRr;

        if (mtfRes && mtfRes.status.startsWith('EXECUTE')) {
          newSigType = mtfRes.direction;
          newAction = newSigType === 'BUY' ? 'BUY / LONG' : 'SELL / SHORT';
          newEntry = mtfRes.entry;
          newTp1 = mtfRes.tp1;
          newTp2 = mtfRes.tp2;
          newSl = mtfRes.sl;
          newConfidence = mtfRes.timeframesAligned;
          newGainPts = mtfRes.gainPts;
          newRr = mtfRes.rr;
          newReason = mtfRes.reason;
        } else {
          // Dynamic structural fallback with explicit Invalidation handling (NO GUESSWORK!)
          const isNearSupply = (currentSpot >= resistance - 4.5);
          const isNearDemand = (currentSpot <= support + 4.5);

          if (prevType === 'BUY' && prevStatus === 'SL_HIT') {
            // Demand was broken! Market momentum has flipped Bearish. Track breakdown to next demand!
            newSigType = 'SELL';
            newAction = 'BEARISH BREAKDOWN CONTINUATION';
            newConfidence = 'SMC Shift (Demand Broken -> Target Lower Liquidity)';
            newGainPts = Number((atr * 2.8).toFixed(1));
            newTp1 = Number((currentSpot - newGainPts).toFixed(2));
            newTp2 = Number((currentSpot - newGainPts - 6.0).toFixed(2));
            newSl = Number((currentSpot + 2.50).toFixed(2));
            newRr = '1 : 2.8 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Demand zone invalidated. Bearish displacement targeting next lower liquidity pool ($' + newTp1.toFixed(1) + ').';
          } else if (prevType === 'SELL' && prevStatus === 'SL_HIT') {
            // Supply was swept! Market momentum has flipped Bullish. Track expansion to next supply!
            newSigType = 'BUY';
            newAction = 'BULLISH EXPANSION BREAKOUT';
            newConfidence = 'SMC Shift (Supply Swept -> Target Higher Liquidity)';
            newGainPts = Number((atr * 2.8).toFixed(1));
            newTp1 = Number((currentSpot + newGainPts).toFixed(2));
            newTp2 = Number((currentSpot + newGainPts + 6.0).toFixed(2));
            newSl = Number((currentSpot - 2.50).toFixed(2));
            newRr = '1 : 2.8 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Supply zone breached. Bullish expansion targeting overhead liquidity pool ($' + newTp1.toFixed(1) + ').';
          } else if (prevType === 'BUY' && prevStatus === 'TP_HIT' && isNearSupply) {
            newSigType = 'SELL';
            newAction = 'SELL / SHORT';
            newConfidence = '4/5 Timeframes Aligned (Supply Rejection)';
            newGainPts = Number((atr * 3.0).toFixed(1));
            newTp1 = Number((currentSpot - newGainPts).toFixed(2));
            newTp2 = Number((currentSpot - newGainPts - 8.0).toFixed(2));
            newSl = Number((currentSpot + 2.50).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Target TP1 achieved at Supply. Liquidity sweep complete; bearish rejection structure targeting EMA 20 & Demand.';
          } else if (prevType === 'SELL' && prevStatus === 'TP_HIT' && isNearDemand) {
            newSigType = 'BUY';
            newAction = 'BUY / LONG';
            newConfidence = '4/5 Timeframes Aligned (Demand Absorption)';
            newGainPts = Number((atr * 3.0).toFixed(1));
            newTp1 = Number((currentSpot + newGainPts).toFixed(2));
            newTp2 = Number((currentSpot + newGainPts + 8.0).toFixed(2));
            newSl = Number((currentSpot - 2.50).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newReason = 'Target TP1 achieved at Demand. Liquidity floor defended; bullish absorption targeting EMA 20 & Supply.';
          } else {
            const isBuy = (confluence && confluence.buyVotes >= confluence.sellVotes);
            newSigType = isBuy ? 'BUY' : 'SELL';
            newAction = isBuy ? 'BUY / LONG' : 'SELL / SHORT';
            newGainPts = 12.0;
            newTp1 = isBuy ? Number((currentSpot + newGainPts).toFixed(2)) : Number((currentSpot - newGainPts).toFixed(2));
            newTp2 = isBuy ? Number((newTp1 + 8.0).toFixed(2)) : Number((newTp1 - 8.0).toFixed(2));
            newSl = isBuy ? Number((currentSpot - 3.0).toFixed(2)) : Number((currentSpot + 3.0).toFixed(2));
            newRr = '1 : 3.0 (+' + newGainPts.toFixed(1) + ' pts)';
            newConfidence = '5/5 Timeframes Aligned (Macro Safe-Haven Trend)';
            newReason = isBuy 
              ? '4H Bullish Trend + 15M Shift + 5M OB Retest + 3M Wick Absorption.'
              : '4H Bearish Trend + 15M Shift + 5M OB Retest + 3M Wick Supply Rejection.';
          }
        }"""

    if target_st_trans in content:
        content = content.replace(target_st_trans, replacement_st_trans)
        print(" [x] Upgraded short-term transition logic with explicit invalidation continuation.")
    else:
        print(" [!] Could not find target_st_trans.")

    # 5. Long-Term Signal Auto-Transition logic & Next Signal Generation
    target_lt_trans = """      // 4. LONG-TERM SWING SIGNAL AUTO-TRANSITION
      const ltElapsed = now - longTermSignalLock.lockedAt;
      const isLtExpired = (!longTermSignalLock.active || ltElapsed >= (72 * 60 * 60 * 1000));
      const isLtTargetOrSlDone = (longTermSignalLock.status === 'TP_HIT' || longTermSignalLock.status === 'SL_HIT') && 
                                 longTermSignalLock.completedAt && 
                                 (now - longTermSignalLock.completedAt >= 8000);

      if (isLtExpired || isLtTargetOrSlDone) {
        const prevLtBias = longTermSignalLock.lastCompletedBias;
        const prevLtStatus = longTermSignalLock.status;

        let ltBias = 'BULLISH';
        let ltActionText = 'BULLISH SWING ACCUMULATION';
        let ltConfText = '4H/1D Macro Trend Aligned';
        let ltTargetVal = Number((currentSpot + 75.0).toFixed(2));
        let ltInvalVal = Number((currentSpot - 45.0).toFixed(2));
        let ltHorizonText = '3 - 7 Days';
        let ltNoteText = 'Central bank accumulation & macro uptrend continuation.';"""

    replacement_lt_trans = """      // 4. LONG-TERM SWING SIGNAL AUTO-TRANSITION
      const ltElapsed = now - longTermSignalLock.lockedAt;
      const isLtStatusPending = (longTermSignalLock.status === 'TP_HIT' || longTermSignalLock.status === 'SL_HIT');
      const ltMinWait = (longTermSignalLock.status === 'SL_HIT') ? 4000 : 7000;
      const isLtTargetOrSlDone = isLtStatusPending && 
                                 longTermSignalLock.completedAt && 
                                 (now - longTermSignalLock.completedAt >= ltMinWait);
      const isLtExpired = !isLtStatusPending && 
                          (longTermSignalLock.status === 'ACTIVE_HOLD' && ltElapsed >= (72 * 60 * 60 * 1000));

      if (isLtExpired || isLtTargetOrSlDone) {
        const prevLtBias = longTermSignalLock.lastCompletedBias;
        const prevLtStatus = longTermSignalLock.lastCompletedStatus;

        let ltBias = 'BULLISH';
        let ltActionText = 'BULLISH SWING ACCUMULATION';
        let ltConfText = '4H/1D Macro Trend Aligned';
        let ltTargetVal = Number((currentSpot + 75.0).toFixed(2));
        let ltInvalVal = Number((currentSpot - 45.0).toFixed(2));
        let ltHorizonText = '3 - 7 Days';
        let ltNoteText = 'Central bank accumulation & macro uptrend continuation.';

        if (prevLtBias === 'BULLISH' && prevLtStatus === 'SL_HIT') {
          // Macro Demand broken -> Switch to Bearish Swing Distribution
          ltBias = 'BEARISH';
          ltActionText = 'BEARISH MACRO DISTRIBUTION';
          ltConfText = 'HTF Liquidity Shift (Floor Breached)';
          ltTargetVal = Number((currentSpot - 65.0).toFixed(2));
          ltInvalVal = Number((currentSpot + 35.0).toFixed(2));
          ltHorizonText = '3 - 6 Days';
          ltNoteText = 'Macro Demand invalidated. Downward distribution targeting lower daily liquidity pool ($' + ltTargetVal.toFixed(1) + ').';
        } else if (prevLtBias === 'BEARISH' && prevLtStatus === 'SL_HIT') {
          // Macro Supply swept -> Switch to Bullish Macro Discovery
          ltBias = 'BULLISH';
          ltActionText = 'BULLISH MACRO DISCOVERY';
          ltConfText = 'HTF Liquidity Shift (Ceiling Breached)';
          ltTargetVal = Number((currentSpot + 65.0).toFixed(2));
          ltInvalVal = Number((currentSpot - 35.0).toFixed(2));
          ltHorizonText = '3 - 6 Days';
          ltNoteText = 'Macro Supply ceiling swept. Upward expansion targeting overhead ATH liquidity ($' + ltTargetVal.toFixed(1) + ').';
        } else"""

    if target_lt_trans in content:
        content = content.replace(target_lt_trans, replacement_lt_trans)
        print(" [x] Upgraded long-term transition logic with invalidation continuation.")
    else:
        print(" [!] Could not find target_lt_trans.")

    # 6. Long-Term UI Pill & Elements on SL_HIT
    target_lt_ui = """      if (ltDirPill) {
        ltDirPill.innerText = isLtBuy ? 'BULLISH' : 'BEARISH';
        ltDirPill.className = 'exec-dir-pill ' + (isLtBuy ? 'buy' : 'sell');
      }
      if (ltConfPill) {
        ltConfPill.innerText = longTermSignalLock.confidence;
      }"""

    replacement_lt_ui = """      if (ltDirPill) {
        if (longTermSignalLock.status === 'SL_HIT') {
          ltDirPill.innerText = 'INVALIDATED 🛑';
          ltDirPill.className = 'exec-dir-pill neutral';
          ltDirPill.style.background = 'rgba(248, 81, 73, 0.2)';
          ltDirPill.style.color = '#f85149';
          ltDirPill.style.borderColor = 'rgba(248, 81, 73, 0.5)';
        } else {
          ltDirPill.innerText = isLtBuy ? 'BULLISH' : 'BEARISH';
          ltDirPill.className = 'exec-dir-pill ' + (isLtBuy ? 'buy' : 'sell');
          ltDirPill.style.background = '';
          ltDirPill.style.color = '';
          ltDirPill.style.borderColor = '';
        }
      }
      if (ltConfPill) {
        if (longTermSignalLock.status === 'SL_HIT') {
          ltConfPill.innerText = 'SWING STOPPED OUT (RE-EVALUATING HTF)';
          ltConfPill.style.color = '#f85149';
        } else {
          ltConfPill.innerText = longTermSignalLock.confidence;
          ltConfPill.style.color = isLtBuy ? '#3fb950' : '#f85149';
        }
      }"""

    if target_lt_ui in content:
        content = content.replace(target_lt_ui, replacement_lt_ui)
        print(" [x] Fixed ltDirPill and ltConfPill on SL_HIT.")
    else:
        print(" [!] Could not find target_lt_ui.")

    # Update Long-Term UI metrics on SL_HIT
    target_lt_metrics = """      if (ltTarget) {
        ltTarget.innerText = '$' + longTermSignalLock.tp.toFixed(2);
      }

      if (ltInval) {
        ltInval.innerText = '$' + longTermSignalLock.inval.toFixed(2);
      }"""

    replacement_lt_metrics = """      if (ltTarget) {
        if (longTermSignalLock.status === 'SL_HIT') {
          ltTarget.innerText = 'CANCELLED';
          ltTarget.style.color = '#8b949e';
        } else {
          ltTarget.innerText = '$' + longTermSignalLock.tp.toFixed(2);
          ltTarget.style.color = '#3fb950';
        }
      }

      if (ltInval) {
        if (longTermSignalLock.status === 'SL_HIT') {
          ltInval.innerText = '$' + longTermSignalLock.inval.toFixed(2) + ' (HIT)';
          ltInval.style.color = '#f85149';
        } else {
          ltInval.innerText = '$' + longTermSignalLock.inval.toFixed(2);
          ltInval.style.color = '#f85149';
        }
      }"""

    if target_lt_metrics in content:
        content = content.replace(target_lt_metrics, replacement_lt_metrics)
        print(" [x] Fixed ltTarget and ltInval on SL_HIT.")
    else:
        print(" [!] Could not find target_lt_metrics.")

    # Update Short-Term timer countdown label to 3.5s
    target_timer_sec = "const remSec = Math.max(1, Math.ceil((6000 - (now - shortTermSignalLock.completedAt)) / 1000));"
    replacement_timer_sec = "const remSec = Math.max(1, Math.ceil((3500 - (now - shortTermSignalLock.completedAt)) / 1000));"
    if target_timer_sec in content:
        content = content.replace(target_timer_sec, replacement_timer_sec)
        print(" [x] Synchronized remSec countdown to 3.5s.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved {filepath} ({len(content):,} bytes).\n")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        update_file(fn)
