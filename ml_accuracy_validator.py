"""
TradingPoint Institutional Machine Learning Accuracy & Win-Rate Validator.
Strict Time-Series Forward-Testing (No Data Leakage) for XAU/USD (Gold) 15-Minute Candles.
Implements 1:2 Risk-to-Reward ($4 TP vs $2 SL) Target Labeling with Random Forest Classifier.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Ensure utf-8 encoding for terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CSV_FILE = "gold_15m_historical.csv"

def load_or_fetch_candles():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        print(f"Loaded {len(df)} candles from local {CSV_FILE}.")
        return df

    import requests
    print("Fetching fresh 1000 candles from Binance PAXGUSDT...")
    r = requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=1000", timeout=10)
    raw = r.json()
    data = []
    for b in raw:
        data.append({
            "timestamp": int(b[0] // 1000),
            "open": float(b[1]),
            "high": float(b[2]),
            "low": float(b[3]),
            "close": float(b[4]),
            "volume": float(b[5])
        })
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(df)} candles to {CSV_FILE}.")
    return df

def run_ml_accuracy_backtest():
    df = load_or_fetch_candles()

    # 1. Feature Engineering
    # (A) EMA 20 Distance
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["dist_ema20"] = df["close"] - df["ema20"]

    # (B) ATR (Average True Range for Volatility, 14 Period)
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()

    # (C) SMC Fair Value Gap (FVG) Signal Feature
    # Bullish FVG: Current candle low > Candle 2-bars ago high AND bullish displacement
    df["is_bullish_fvg"] = ((df["low"] > df["high"].shift(2)) & (df["close"].shift(1) > df["open"].shift(1))).astype(int)

    # (D) Candle Body vs Wick Ratio
    df["body_size"] = (df["close"] - df["open"]).abs()
    df["candle_range"] = df["high"] - df["low"]
    df["body_ratio"] = df["body_size"] / (df["candle_range"] + 1e-5)

    # (E) Volume Spike Feature
    df["vol_sma"] = df["volume"].rolling(20).mean()
    df["vol_surge"] = (df["volume"] > df["vol_sma"] * 1.5).astype(int)

    # 2. Target Labeling (Institutional 1:2 Risk to Reward)
    # Check: Kya agli 4 candles (1 hour window) mein price +4 USD upar gayi (TP) bina -2 USD giray (SL)?
    tp_dist = 4.0   # $4.00 TP per oz
    sl_dist = 2.0   # $2.00 SL per oz

    labels = []
    forward_candles_count = 4
    total_bars = len(df)

    for i in range(total_bars - forward_candles_count):
        entry_price = df["close"].iloc[i]
        future_candles = df.iloc[i + 1 : i + 1 + forward_candles_count]
        
        hit_tp = (future_candles["high"] >= entry_price + tp_dist).any()
        hit_sl = (future_candles["low"] <= entry_price - sl_dist).any()
        
        if hit_tp and not hit_sl:
            labels.append(1)  # Successful Win
        else:
            labels.append(0)  # Loss / Failed Setup

    labels.extend([np.nan] * forward_candles_count)
    df["target"] = labels
    df = df.dropna().copy()

    # 3. Feature Matrix (X) & Target (y)
    feature_cols = ["dist_ema20", "atr", "is_bullish_fvg", "body_ratio", "vol_surge"]
    X = df[feature_cols]
    y = df["target"].astype(int)

    # 4. Strict Time-Series Split (70% Train, 30% Test - Forward Out-Of-Sample, Zero Data Leakage)
    split_idx = int(len(df) * 0.70)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Total Valid Bars: {len(df)}")
    print(f"Training Bars (Past 70%): {len(X_train)} | Testing Bars (Forward 30%): {len(X_test)}")
    print(f"Class Distribution in Test Set: Win (1) = {int(y_test.sum())}, Loss/Pass (0) = {len(y_test) - int(y_test.sum())}")

    # 5. Model Training (Institutional Random Forest Classifier)
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=6,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Feature Importances
    importances = model.feature_importances_
    feat_rank = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

    # 6. Predictions & Accuracy Metrics
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    total_accuracy = accuracy_score(y_test, y_pred) * 100
    win_rate_precision = precision_score(y_test, y_pred, zero_division=0) * 100
    rec = recall_score(y_test, y_pred, zero_division=0) * 100
    f1 = f1_score(y_test, y_pred, zero_division=0) * 100
    conf_matrix = confusion_matrix(y_test, y_pred)

    # 7. Probability Threshold Filter (High Conviction Confluence)
    # Filter 1: Probability >= 0.60
    trades_60 = (y_prob >= 0.60).astype(int)
    prec_60 = precision_score(y_test, trades_60, zero_division=0) * 100
    count_60 = int(trades_60.sum())

    # Filter 2: Probability >= 0.70 (High Conviction Threshold)
    trades_70 = (y_prob >= 0.70).astype(int)
    prec_70 = precision_score(y_test, trades_70, zero_division=0) * 100
    count_70 = int(trades_70.sum())

    # Filter 3: Probability >= 0.75 (Institutional Super Conviction)
    trades_75 = (y_prob >= 0.75).astype(int)
    prec_75 = precision_score(y_test, trades_75, zero_division=0) * 100
    count_75 = int(trades_75.sum())

    print("\n" + "=" * 55)
    print("📊 MACHINE LEARNING MODEL BACKTEST ACCURACY REPORT")
    print("=" * 55)
    print(f"Asset / Timeframe             : XAU/USD (Gold) | 15-Minute")
    print(f"Risk-to-Reward Ratio (R:R)    : 1:2 ($4.00 TP vs $2.00 SL)")
    print(f"Validation Method             : Strict Forward Time-Series Split (Zero Leakage)")
    print("-" * 55)
    print(f"Overall Directional Accuracy  : {total_accuracy:.2f}%")
    print(f"Standard Model Win-Rate (0.50): {win_rate_precision:.2f}% (Precision)")
    print(f"Signal Recall (Opportunity)   : {rec:.2f}%")
    print(f"F1 Balanced Score             : {f1:.2f}%")
    print("-" * 55)
    print("🎯 CONFLUENCE PROBABILITY THRESHOLD SCALING:")
    print(f"  • Prob >= 50% (Standard)    : Win-Rate = {win_rate_precision:.2f}% ({int(y_pred.sum())} trades)")
    print(f"  • Prob >= 60% (Moderate)    : Win-Rate = {prec_60:.2f}% ({count_60} trades)")
    print(f"  • Prob >= 70% (High Conv.)  : Win-Rate = {prec_70:.2f}% ({count_70} trades)")
    print(f"  • Prob >= 75% (Super Conv.) : Win-Rate = {prec_75:.2f}% ({count_75} trades)")
    print("-" * 55)
    print("🧩 CONFUSION MATRIX (Standard Threshold):")
    print(f"  Losses Correctly Predicted (TN) : {conf_matrix[0][0]}")
    print(f"  False Alarm Buys (FP)           : {conf_matrix[0][1]}")
    print(f"  Missed Winning Trades (FN)      : {conf_matrix[1][0]}")
    print(f"  Confirmed Winning Trades (TP)   : {conf_matrix[1][1]}")
    print("-" * 55)
    print("🏆 FEATURE IMPORTANCE BREAKDOWN:")
    for feat, imp in feat_rank:
        bar = "█" * int(imp * 30)
        print(f"  {feat:15} : {imp*100:5.2f}% {bar}")
    print("=" * 55)

    return {
        "accuracy": total_accuracy,
        "win_rate_standard": win_rate_precision,
        "win_rate_70": prec_70,
        "win_rate_75": prec_75,
        "conf_matrix": conf_matrix.tolist()
    }

if __name__ == "__main__":
    run_ml_accuracy_backtest()
