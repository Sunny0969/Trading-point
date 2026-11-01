"""
Refactor gold_dashboard.html, index.html, and deep_analysis_gold.html
to achieve 100% mobile responsiveness inspired by TradingView and Exness mobile app layouts.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def test_anchors(filepath):
    print(f"Testing anchors in {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    anchors = [
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        'LightweightCharts.createChart(container, {',
        'function selectTimeframe(tf) {',
        'class="terminal-nav-left"',
        '<div id="view-terminal">',
        'function renderDemoWalletUI(spotPrice) {',
        'function renderDemoPositionsList() {'
    ]

    for a in anchors:
        if a in content:
            print(f" [x] Found: {a[:50]}...")
        else:
            print(f" [!] Missing: {a[:50]}...")

if __name__ == '__main__':
    test_anchors('gold_dashboard.html')
