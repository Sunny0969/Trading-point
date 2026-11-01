with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- Around line 265 ---")
for i in range(262, 275):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Around line 860 ---")
for i in range(855, 870):
    print(f"{i+1}: {lines[i]}", end='')
