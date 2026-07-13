# brain.py — Your Local AI Second Brain Controller
# Usage: python brain.py [ingest|query|lint|mirror|digest|decision|moc]

import os, sys, json, datetime, requests, glob

# ── CONFIGURATION ───────────────────────────────────────────
VAULT_PATH = os.path.expanduser(r"C:/Users/Rehan/second-brain")
MODEL = "qwen2.5:14b"   # safer for your system (change to 14b later if needed)
OLLAMA_URL = "http://localhost:11434/api/generate"
MAX_CHARS = 12000

# ── PATHS ───────────────────────────────────────────────────
RAW = os.path.join(VAULT_PATH, "raw-sources")
WIKI = os.path.join(VAULT_PATH, "wiki")
MOC = os.path.join(VAULT_PATH, "moc")
INDEX = os.path.join(WIKI, "index.md")
LOG = os.path.join(WIKI, "log.md")
SCHEMA = os.path.join(VAULT_PATH, "CLAUDE.md")

# ── FILE HELPERS ────────────────────────────────────────────
def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return ''

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[wrote] {os.path.relpath(path, VAULT_PATH)}')

def append_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write('\n' + content)

def truncate(text, limit=None):
    n = limit or MAX_CHARS
    return text[:n] + '\n[...truncated...]' if len(text) > n else text

def today():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def get_logged_files():
    log = read_file(LOG)
    return [l.split('| source:')[1].strip()
            for l in log.split('\n') if '| source:' in l]

def get_new_raw_file():
    logged = get_logged_files()
    for f in sorted(glob.glob(os.path.join(RAW, '**/*'), recursive=True),
                    key=os.path.getmtime, reverse=True):
        if os.path.isfile(f) and os.path.basename(f) not in logged:
            return f
    return None

# ── OLLAMA API ──────────────────────────────────────────────
def ask(prompt):
    print('[model thinking — streaming output below]')
    print('-' * 50)

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True
        }, stream=True, timeout=600)

        result = ''
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                chunk = data.get('response', '')
                result += chunk
                print(chunk, end='', flush=True)
                if data.get('done'):
                    break

        print('\n' + '-' * 50)
        return result.strip()

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama.")
        sys.exit(1)

# ── PARSE OUTPUT ────────────────────────────────────────────
def parse_and_write(response, source_name):
    sections = response.split("=== FILE:")
    written = []

    for section in sections[1:]:
        lines = section.strip().split('\n')
        rel_path = lines[0].strip().rstrip('=').strip()
        full_path = os.path.join(VAULT_PATH, rel_path)

        body = []
        for line in lines[1:]:
            if line.strip() == "=== END FILE ===":
                break
            body.append(line)

        content = '\n'.join(body).strip()

        if content and rel_path:
            write_file(full_path, content)
            written.append(rel_path)

    if written:
        log_entry = f"\n## {today()} | source: {os.path.basename(source_name)}"
        log_entry += f"\nFiles: {len(written)}"
        log_entry += ''.join(f'\n- {w}' for w in written)

        append_file(LOG, log_entry)
        print(f"\nDone. {len(written)} file(s) written.")
    else:
        print("\n[No === FILE: === blocks found]")

# ── OPERATIONS ──────────────────────────────────────────────
def op_query(question):
    print("\n=== QUERY ===")

    index = truncate(read_file(INDEX), 4000)
    schema = read_file(SCHEMA)

    prompt = f"""
You are a knowledge assistant.

Rules:
{schema}

WIKI INDEX:
{index}

QUESTION:
{question}

Answer using the wiki.
"""

    ask(prompt)

# ── MAIN ────────────────────────────────────────────────────
def main():
    cmds = {
        "query": (op_query, 1, 'python brain.py query "your question"'),
    }

    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print("brain.py — Local AI Second Brain")
        print("\nCommands:")
        for k, (_, _, desc) in cmds.items():
            print(f"  python brain.py {k:<10} {desc}")
        return

    op, needs_arg, _ = cmds[sys.argv[1]]

    if needs_arg and len(sys.argv) < 3:
        print("Missing argument")
        return

    arg = ' '.join(sys.argv[2:]) if needs_arg else None
    op(arg) if arg else op()

if __name__ == "__main__":
    main()