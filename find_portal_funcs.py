with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'switchPortalView' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
    if 'checkUrlForTerminal' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
