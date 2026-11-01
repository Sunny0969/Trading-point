import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- Lines 275-305 (Portal View Router) ---")
for i in range(275, 305):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')

print("\n--- Lines 4295-4385 (traderAdminSidebar HTML) ---")
for i in range(4295, 4385):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')

print("\n--- Lines 5225-5285 (Trader Dashboard View) ---")
for i in range(5225, 5285):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')
