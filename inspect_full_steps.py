import json, sys
sys.stdout.reconfigure(encoding='utf-8')

t_path = r'C:\Users\SP\.gemini\antigravity\brain\7f0a9a8e-2615-4ca6-8352-355424ad1b6f\.system_generated\logs\transcript_full.jsonl'
with open(t_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in [3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668]:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for tc in tool_calls:
                fn = tc.get('function', {}).get('name')
                args = tc.get('function', {}).get('arguments')
                print(f"Line {idx} Tool: {fn}")
                if fn in ['write_file', 'edit_file']:
                    print("  Path:", args.get('Path'))
                    if 'profile' in str(args.get('Path')):
                        print("  Target:", args.get('Target'))
                elif fn == 'run_command':
                    print("  Command:", args.get('CommandLine'))
            txt = data.get('content', '')
            if txt:
                print(f"Line {idx} Text:", txt[:300])
