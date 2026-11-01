import os, json, sys

sys.stdout.reconfigure(encoding='utf-8')
t_path = r'C:\Users\SP\.gemini\antigravity\brain\7f0a9a8e-2615-4ca6-8352-355424ad1b6f\.system_generated\logs\transcript.jsonl'
with open(t_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            print('USER_INPUT:', data.get('content'))
        elif data.get('type') == 'PLANNER_RESPONSE':
            tool_calls = data.get('tool_calls', [])
            for tc in tool_calls:
                fn = tc.get('function', {}).get('name')
                args = tc.get('function', {}).get('arguments')
                if fn in ['write_file', 'edit_file']:
                    print(f"Tool {fn}: {args.get('Path')}")
                elif fn == 'run_command':
                    cmd = args.get('CommandLine', '')
                    if 'git' in cmd or 'copy' in cmd:
                        print(f"Command: {cmd}")
