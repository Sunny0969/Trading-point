import json

transcript_path = r'C:\Users\SP\.gemini\antigravity\brain\0f95f872-177c-4445-abf8-72f5503b719b\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'trader_admin_panel' in line or 'trader_dashboard' in line:
            data = json.loads(line)
            print(f"Step {data.get('step_index')}: type={data.get('type')}")
            content = str(data.get('content', ''))
            print(content[:400])
            print("="*60)
