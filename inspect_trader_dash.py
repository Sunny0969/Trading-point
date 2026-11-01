with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(5220, 5290):
    print(f"{i+1}: {lines[i]}", end='')
