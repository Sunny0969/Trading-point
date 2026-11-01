import os, json, sys

sys.stdout.reconfigure(encoding='utf-8')
t_path = r'C:\Users\SP\.gemini\antigravity\brain\7f0a9a8e-2615-4ca6-8352-355424ad1b6f\.system_generated\logs\transcript.jsonl'
lines = []
with open(t_path, 'r', encoding='utf-8') as f:
    for line in f:
        lines.append(json.loads(line))

# Print the last 15 steps
for data in lines[-15:]:
    step = data.get('step_index')
    t = data.get('type')
    src = data.get('source')
    print(f"Step {step} | {t} | {src}")
    if t == 'USER_INPUT':
        print("  User Input:", data.get('content'))
    elif t == 'PLANNER_RESPONSE':
        txt = data.get('content', '')
        if txt:
            print("  Response:", txt[:200])
        tool_calls = data.get('tool_calls', [])
        for tc in tool_calls:
            print("  Tool Call:", tc.get('function', {}).get('name'), tc.get('function', {}).get('arguments'))
    elif t == 'GENERIC':
        out = data.get('content', '')
        if out and len(out) < 200:
            print("  Output:", out)
