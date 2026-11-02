files = ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']
for fname in files:
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Update dropdown bold text to exact match
    text = text.replace(
        '<b style="color: #e879f9;">⚡ SMC Inducement &amp; CHoCH Supply Sniper</b>',
        '<b style="color: #e879f9;">⚡ SMC Inducement &amp; CHoCH Supply Sniper (CHoCH + EQL + Supply Tap)</b>'
    )

    # 2. Update reason in evaluateSMC_InducementSupply
    old_target = "reason: `Bearish CHoCH confirmed. Intermediate buyers trapped at Inducement (X) $${inducementHigh.toFixed(2)}. Extreme Supply Zone ($${supplyLow.toFixed(2)}-$${supplyHigh.toFixed(2)}) mitigated with rejection. Targeting EQL liquidity pool.`"
    new_target = 'reason: "Bearish CHoCH confirmed. Intermediate buyers trapped at Inducement (X). Extreme Supply Zone mitigated with rejection. Targeting EQL liquidity pool."'
    if old_target in text:
        text = text.replace(old_target, new_target)

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Polished {fname}")
