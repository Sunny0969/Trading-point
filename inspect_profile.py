with open('profile.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("sidebar in profile.html:", len(re.findall(r'sidebar', text, re.IGNORECASE)))
print("admin in profile.html:", len(re.findall(r'admin', text, re.IGNORECASE)))

# Print headings and navigation items in profile.html
for line in text.splitlines():
    if any(k in line for k in ['<h1', '<h2', '<h3', '<nav', '<aside', 'sidebar', 'Admin', 'Trader']):
        print(line.strip())
