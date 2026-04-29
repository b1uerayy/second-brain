# ─────────────────────────────────────────────────────────────
# brain.py — Your Local AI Second Brain Controller
# Usage: python3 brain.py [ingest|query|lint|mirror|digest|decision|moc]
# Needs: Python 3.8+, Ollama running, requests library
# Install: pip3 install requests --break-system-packages
# ─────────────────────────────────────────────────────────────
import os, sys, json, datetime, requests, glob
# ── CONFIGURATION — edit these to match your setup ──────────
VAULT_PATH = os.path.expanduser(r"C:\Users\Rehan\second-brain") # path to your vault
MODEL = "qwen2.5:14b" # your downloaded model
OLLAMA_URL = "http://localhost:11434/api/generate"
MAX_CHARS = 12000 # reduce to 6000 if slow, raise to 16000 if fast
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
 print(f' [wrote] {os.path.relpath(path, VAULT_PATH)}')
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
 for f in sorted(glob.glob(os.path.join(RAW,'**/*'), recursive=True),
 key=os.path.getmtime, reverse=True):
 if os.path.isfile(f) and os.path.basename(f) not in logged:
return f
 return None
# ── OLLAMA API CALL ─────────────────────────────────────────
def ask(prompt):
 print(' [model thinking — streaming output below]', flush=True)
 print('-' * 50)
 try:
 resp = requests.post(OLLAMA_URL, json={
 "model": MODEL, "prompt": prompt, "stream": True
 }, stream=True, timeout=600)
 result = ''
 for line in resp.iter_lines():
 if line:
 data = json.loads(line)
 chunk = data.get('response', '')
 result += chunk
 print(chunk, end='', flush=True)
 if data.get('done'): break
 print('\n' + '-' * 50)
 return result.strip()
 except requests.exceptions.ConnectionError:
 print("ERROR: Cannot connect to Ollama.")
 print("Start Ollama first (menu bar / system tray / systemctl).")
 sys.exit(1)
# ── PARSE MODEL OUTPUT AND WRITE FILES ──────────────────────
def parse_and_write(response, source_name):
 sections = response.split("=== FILE:")
 written = []
 for section in sections[1:]:
 lines = section.strip().split('\n')
 rel_path = lines[0].strip().rstrip('=').strip()
 full_path = os.path.join(VAULT_PATH, rel_path)
 body = []
 for line in lines[1:]:
 if line.strip() in ("=== END FILE ===", "") and not body:
 continue
 if line.strip() == "=== END FILE ===": break
 body.append(line)
 content = '\n'.join(body).strip()
 if content and rel_path:
 write_file(full_path, content)
 written.append(rel_path)
 if written:
 log_entry = (f'\n## {today()} | source: {os.path.basename(source_name)}'
 + f'\nFiles: {len(written)}'
+ ''.join(f'\n- {w}' for w in written))
 append_file(LOG, log_entry)
 print(f"\nDone. {len(written)} file(s) written.")
 else:
 print("\n[No === FILE: === blocks found in response]")
 print("For query/digest this is normal. For ingest, try a larger model.")
# ── OPERATIONS ──────────────────────────────────────────────
def op_ingest():
 print("\n=== INGEST ===")
 f = get_new_raw_file()
 if not f:
 print("No new files in raw-sources/. Add a file and try again.")
 return
 name = os.path.basename(f)
 src = truncate(read_file(f))
 schema = read_file(SCHEMA)
 index = truncate(read_file(INDEX), 3000)
 print(f" Processing: {name}")
 prompt = f'''You are a wiki maintainer. Rules:\n{schema}
SOURCE FILE: {name}
CONTENT:
{src}
CURRENT WIKI INDEX:
{index}
TASK - INGEST OPERATION:
1. Write a wiki summary page. Use this exact format:
 === FILE: wiki/{name.replace('
','_').replace('.txt','').replace('.md','')}_summary.md ===
 [full markdown content with YAML frontmatter and [[wiki-links]]]
 === END FILE ===
2. Update index.md to include the new page:
 === FILE: wiki/index.md ===
 [full updated index.md content]
 === END FILE ===
Write the files now. Use === FILE: path === and === END FILE === exactly.'''
 response = ask(prompt)
 parse_and_write(response, name)
def op_query(question):
 print("\n=== QUERY ===")
 index = truncate(read_file(INDEX), 4000)
 schema = read_file(SCHEMA)
 prompt = f'''You are a knowledge assistant. Rules:\n{schema}
WIKI INDEX:
{index}
QUESTION: {question}
Answer using the wiki index. Cite which pages your answer draws from.
If the wiki lacks information, say so and suggest what to add.'''
 ask(prompt)
def op_lint():
 print("\n=== LINT ===")
 schema = read_file(SCHEMA)
 files = glob.glob(os.path.join(WIKI, '**/*.md'), recursive=True)[:30]
 content = ''
 for fp in files:
 rel = os.path.relpath(fp, VAULT_PATH)
 content += f'\n=== {rel} ===\n' + truncate(read_file(fp), 800)
 prompt = f'''You are a wiki health checker. Rules:\n{schema}
WIKI SAMPLE:
{content}
TASK - LINT OPERATION:
Find problems: contradictions, orphan pages, missing concepts,
outdated claims, isolated pages. Write a full report.
Use this format:
=== FILE: wiki/lint-report.md ===
# Wiki Health Report — [DATE]
## Critical Issues
## Medium Issues
## Minor Issues
## Top 3 Things To Fix First
=== END FILE ==='''
 response = ask(prompt)
 parse_and_write(response, '_lint_')
def op_mirror():
 print("\n=== THINKING MIRROR ===")
 schema = read_file(SCHEMA)
 files = glob.glob(os.path.join(WIKI, '**/*.md'), recursive=True)[:25]
 content = ''
 for fp in files:
 rel = os.path.relpath(fp, VAULT_PATH)
 content += f'\n=== {rel} ===\n' + truncate(read_file(fp), 600)
 prompt = f'''You are a thinking analyst. Rules:\n{schema}
WIKI:
{content}
TASK - THINKING MIRROR:
Find: recurring beliefs, hidden assumptions, self-contradictions,
obsessive topics, strongest mental models, blind spots.
Be specific. Cite which wiki pages each observation comes from.
Format:
=== FILE: wiki/thinking-mirror.md ===
# Thinking Mirror — [DATE]
[candid analysis]
=== END FILE ==='''
 response = ask(prompt)
 parse_and_write(response, '_mirror_')
def op_digest():
 print("\n=== MORNING DIGEST ===\n")
 tracker = truncate(read_file(os.path.join(WIKI, 'action-tracker.md')), 2000)
 log = read_file(LOG)
 lint = truncate(read_file(os.path.join(WIKI, 'lint-report.md')), 1000)
 print(f"Date: {today()}")
 if tracker:
 q = f'List tasks due today or overdue. Be brief.\n\n{tracker}'
 print("\n-- OPEN TASKS --")
 ask(q)
 recent = [l for l in log.split('\n') if 'ingest' in l.lower()][-5:]
 print("\n-- RECENT INGESTS --")
 for line in recent: print(' ', line.strip())
 if lint:
 print("\n-- WIKI HEALTH --")
 ask(f'List the top 3 wiki issues in one line each.\n\n{lint}')
def op_decision(topic):
 print("\n=== DECISION ENGINE ===")
 schema = read_file(SCHEMA)
 dlog = truncate(read_file(os.path.join(WIKI, 'decision-log.md')), 3000)
 index = truncate(read_file(INDEX), 2000)
 slug = topic[:30].replace(' ','_')
 prompt = f'''Decision analyst using only the person's
history.\nRules:\n{schema}
PAST DECISIONS: {dlog}
WIKI INDEX: {index}
DECISION: {topic}
Write a decision brief using only my own history. Include:
1. What my past says about this type of decision
2. Beliefs I hold that are relevant
3. What I tend to get right/wrong
4. The key question I might be avoiding
Format:
=== FILE: wiki/decisions/{slug}.md ===
[brief]
=== END FILE ==='''
 response = ask(prompt)
 parse_and_write(response, '_decision_')
def op_moc(topic):
 print(f"\n=== MAP OF CONTENT: {topic} ===")
 schema = read_file(SCHEMA)
 index = truncate(read_file(INDEX), 4000)
 slug = topic.lower().replace(' ', '-')
 prompt = f'''Knowledge cartographer.\nRules:\n{schema}
WIKI INDEX: {index}
TOPIC: {topic}
Create a Map of Content. Include:
1. 2-paragraph overview of what I know about this topic
2. All related wiki pages with [[links]] and one-line descriptions, grouped by
sub-theme
3. Top 3 most important pages highlighted
4. Top 3 knowledge gaps
5. 3 specific sources to find next
Format:
=== FILE: moc/{slug}-moc.md ===
[content]
=== END FILE ==='''
 response = ask(prompt)
 parse_and_write(response, '_moc_')
# ── MAIN ────────────────────────────────────────────────────
def main():
 cmds = {
 "ingest": (op_ingest, 0, "Process newest file in raw-sources/"),
 "query": (op_query, 1, 'python3 brain.py query "your question"'),
 "lint": (op_lint, 0, "Weekly wiki health check"),
 "mirror": (op_mirror, 0, "Monthly thinking pattern analysis"),
 "digest": (op_digest, 0, "Morning summary of tasks and activity"),
 "decision": (op_decision, 1, 'python3 brain.py decision "describe
decision"'),
 "moc": (op_moc, 1, 'python3 brain.py moc "topic name"'),
 }
 if len(sys.argv) < 2 or sys.argv[1] not in cmds:
 print("brain.py — Local AI Second Brain")
 print("\nCommands:")
 for k, (_, _, desc) in cmds.items():
 print(f" python3 brain.py {k:<12} {desc}")
 return
 op, needs_arg, _ = cmds[sys.argv[1]]
 if needs_arg and len(sys.argv) < 3:
 print(f"This command needs an argument. See usage above.")
 return
 arg = ' '.join(sys.argv[2:]) if needs_arg else None
 op(arg) if arg else op()
if __name__ == "__main__":
 main()
