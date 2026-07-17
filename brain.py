# =============================================================================
#  brain.py — Local AI Second Brain Controller
#  Version: 1.0
#
#  Usage:
#    python3 brain.py ingest              → process newest file from raw-sources/
#    python3 brain.py query "question"   → ask your knowledge base anything
#    python3 brain.py lint               → weekly wiki health check
#    python3 brain.py mirror             → monthly thinking pattern analysis
#    python3 brain.py digest             → morning summary of tasks & activity
#    python3 brain.py decision "topic"   → decision brief from your own history
#    python3 brain.py moc "topic"        → create a Map of Content page
#
#  Requirements:
#    - Python 3.8+
#    - Ollama running (ollama.com)
#    - pip3 install requests --break-system-packages
# =============================================================================

import os
import sys
import json
import datetime
import glob
import re
import embedding_engine
import retrieval_engine

def safe_filename(name):
    """Convert filenames into safe wiki filenames."""
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^\w\- ]", "", name)
    return name.replace(" ", "_")


def today():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found.")
    print("Fix: pip3 install requests --break-system-packages")
    sys.exit(1)


# =============================================================================
#  CONFIGURATION — edit these to match your setup
# =============================================================================

VAULT_PATH = os.path.expanduser(r"C:\Users\Rehan\second-brain")   # path to your Obsidian vault
MODEL      = "qwen2.5:7b"                   # your downloaded Ollama model
                                              # run 'ollama list' to see options
OLLAMA_URL = "http://localhost:11434/api/generate"
MAX_CHARS  = 6000  # max characters sent per request
                    # lower to 6000 if slow, raise to 16000 if fast machine


# =============================================================================
#  PATHS — do not edit these
# =============================================================================

RAW    = os.path.join(VAULT_PATH, "raw-sources")
WIKI   = os.path.join(VAULT_PATH, "wiki")
MOC    = os.path.join(VAULT_PATH, "moc")
INDEX  = os.path.join(WIKI, "index.md")
LOG    = os.path.join(WIKI, "log.md")
SCHEMA = os.path.join(VAULT_PATH, "CLAUDE.md")


# =============================================================================
#  FILE HELPERS
# =============================================================================

def read_file(path):
    """Read a file and return its contents. Returns empty string if not found."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_file(path, content):
    """Write content only if it has changed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        old = read_file(path)
        if old == content:
            print(f"  [unchanged] {os.path.relpath(path, VAULT_PATH)}")
            return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [wrote]      {os.path.relpath(path, VAULT_PATH)}")
    return True


def append_file(path, content):
    """Append content to a file, creating it if it doesn't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content)
    print(f"  [appended] {os.path.relpath(path, VAULT_PATH)}")


def truncate(text, limit=None):
    """Truncate text to MAX_CHARS (or custom limit) to stay within context window."""
    n = limit or MAX_CHARS
    if len(text) > n:
        return text[:n] + "\n\n[...content truncated to fit context window...]"
    return text



# =============================================================================
#  LOG TRACKING — so brain.py knows which files have already been ingested
# =============================================================================

def get_logged_filenames():
    """Return list of filenames already recorded in wiki/log.md."""
    log = read_file(LOG)
    logged = []
    for line in log.split("\n"):
        if "| source:" in line:
            logged.append(line.split("| source:")[1].strip())
    return logged


def get_all_new_raw_files():
    """Return every uningested file, newest first."""
    logged = set(get_logged_filenames())

    files = [
        f for f in glob.glob(os.path.join(RAW, "**/*"), recursive=True)
        if os.path.isfile(f)
        and os.path.basename(f) not in logged
    ]

    files.sort(key=os.path.getmtime, reverse=True)
    return files


def append_log(source_name, written_files):
    """Append a record of this operation to wiki/log.md."""
    entry = f"\n## {today()} | source: {os.path.basename(source_name)}"
    entry += f"\nFiles written: {len(written_files)}"
    for f in written_files:
        entry += f"\n- {f}"
    append_file(LOG, entry)


# =============================================================================
#  OLLAMA — sends prompts to your local model and streams the response
# =============================================================================

def ask(prompt, silent=False):
    """
    Send a prompt to the local Ollama model.
    Streams the response character by character.
    Returns the full response as a string.
    """
    if not silent:
        print("\n" + "─" * 60)
        print(f"  Model: {MODEL}  |  Thinking...")
        print("─" * 60)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=600  # 10 minute timeout for long operations
        )
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                chunk = data.get("response", "")
                full_response += chunk
                if not silent:
                    print(chunk, end="", flush=True)
                if data.get("done"):
                    break

        if not silent:
            print("\n" + "─" * 60)

        return full_response.strip()

    except requests.exceptions.ConnectionError:
        print("\n  ERROR: Cannot connect to Ollama.")
        print("  Fix:   Make sure Ollama is running.")
        print("         Mac    → open Applications > Ollama (menu bar icon)")
        print("         Windows → search Ollama in Start menu")
        print("         Linux  → sudo systemctl start ollama")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print("\n  ERROR: Ollama timed out (took longer than 10 minutes).")
        print("  Fix:   Lower MAX_CHARS in brain.py, or switch to a smaller model.")
        sys.exit(1)

    except Exception as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)


# =============================================================================
#  RESPONSE PARSER — extracts file blocks from model output and writes them
# =============================================================================

def parse_and_write(response, source_name):
    """
    Parse the model's response for === FILE: path === blocks.
    Write each block to the correct path in the vault.
    Log the operation to wiki/log.md.

    The model is instructed to format file writes like this:
        === FILE: wiki/some-page.md ===
        [file content here]
        === END FILE ===
    """
    if "=== FILE:" not in response:
        print("\n⚠ Model did not generate any file blocks.")
        return
    
    sections = response.split("=== FILE:")
    written = []

    for section in sections[1:]:
        lines = section.strip().split("\n")

        # First line is the file path (strip trailing === if present)
        rel_path = lines[0].strip().rstrip("=").strip()
        if not rel_path:
            continue

        full_path = os.path.join(VAULT_PATH, rel_path)

        # Collect content lines until === END FILE ===
        body = []
        for line in lines[1:]:
            if line.strip() == "=== END FILE ===":
                break
            body.append(line)

        content = "\n".join(body).strip()

        if content and rel_path:
           if write_file(full_path, content):
                written.append(rel_path)
                # Update embedding automatically
                if rel_path.startswith("wiki/"):

                    if not rel_path.endswith("index.md") and not rel_path.endswith("log.md"):

                        embedding_engine.update_embedding(full_path)

    if written:
        print(f"\n  ✓ Done. {len(written)} file(s) written to vault.")
        append_log(source_name, written)
    else:
        print("\n  [No === FILE: === blocks found in model response]")
        print("  For query and digest operations this is normal.")
        print("  For ingest/lint/mirror — try a larger model (7b or 8b).")
        print("  You can also add this to CLAUDE.md:")
        print("  'CRITICAL: Always wrap file output in === FILE: path === and === END FILE ==='")


# =============================================================================
#  OPERATION: INGEST
#  Reads the newest unprocessed file from raw-sources/ and builds wiki pages
# =============================================================================

def op_ingest():
    print("\n" + "=" * 60)
    print("  INGEST — processing newest file from raw-sources/")
    print("=" * 60)

    # Find the next file to process
    files = get_all_new_raw_files()

    if not files:
        print("\n  No new files found in raw-sources/.")
        print("  Either all files have been ingested, or raw-sources/ is empty.")
        return

    source_file = files[0]   # newest file
    

    name    = os.path.basename(source_file)
    raw = read_file(source_file)

    if len(raw) > MAX_CHARS:
        print("  ⚠ Large source detected. Content was truncated.")

    content = truncate(raw)
    schema  = read_file(SCHEMA)
    index   = truncate(read_file(INDEX), 3000)

    print(f"\n  Processing: {name}")
    print(f"  Characters: {len(content):,}")

    prompt = f"""You are a disciplined wiki maintainer. Follow these rules exactly:
{schema}

---
SOURCE FILE NAME: {name}

SOURCE CONTENT:
{content}

---
CURRENT WIKI INDEX:
{index}

---
TASK — INGEST OPERATION:

Step 1: Write a summary wiki page for this source.
Use this EXACT format (do not skip the markers):

=== FILE: wiki/{safe_filename(name)}_summary.md ===
---
tags: [add relevant tags here]
date_created: {today()[:10]}
last_updated: {today()[:10]}
source: {name}
---

# [Title of the source]

## Summary
[2-3 paragraph summary of the key ideas]

## Key Concepts
[bullet list of the most important concepts]

## Connections
[List 3-5 [[wiki-links]] to related concepts that should exist in the wiki]

## Quotes Worth Keeping
[1-3 notable quotes or ideas from the source, using > blockquote format]
=== END FILE ===

Step 2: Update wiki/index.md to include this new page.
Preserve all existing content. Just add a new line for the new page.

=== FILE: wiki/index.md ===
[full updated index.md — preserve existing lines, add new entry at the bottom]
=== END FILE ===

Write both files now. Use the === FILE: === markers exactly as shown."""

    response = ask(prompt)
    parse_and_write(response, name)

# =============================================================================
#  OPERATION: INGEST ALL
#  Processes every unprocessed file in raw-sources/
# =============================================================================

def op_ingest_all():
    print("\n" + "=" * 60)
    print("  INGEST-ALL — processing every unprocessed file")
    print("=" * 60)

    processed = 0

    files = get_all_new_raw_files()
    total = len(files)

    if total == 0:
        print("\nNo new files to ingest.")
        return

    processed = 0
    success = []
    failed = []
    schema = read_file(SCHEMA)
    index = truncate(read_file(INDEX), 3000)

    for i, source_file in enumerate(files, start=1):

        name = os.path.basename(source_file)

        print("\n" + "=" * 60)
        print(f"[{i}/{total}] Processing: {name}")
        print("=" * 60)
        raw = read_file(source_file)

        if len(raw) > MAX_CHARS:
            print("  ⚠ Large source detected. Content was truncated.")

        content = truncate(raw)
        

        print(f"    Characters: {len(content):,}")

        prompt = f"""You are a disciplined wiki maintainer. Follow these rules exactly:
{schema}

---
SOURCE FILE NAME: {name}

SOURCE CONTENT:
{content}

---
CURRENT WIKI INDEX:
{index}

---
TASK — INGEST OPERATION:

Step 1: Write a summary wiki page for this source.

Use this EXACT format:

=== FILE: wiki/{safe_filename(name)}_summary.md ===
---
tags: [add relevant tags here]
date_created: {today()[:10]}
last_updated: {today()[:10]}
source: {name}
---

# [Title]

## Summary
[2-3 paragraph summary]

## Key Concepts
[bullet list]

## Connections
[3-5 [[wiki-links]]]

## Quotes Worth Keeping
[1-3 quotes]

=== END FILE ===

Step 2: Update wiki/index.md.

=== FILE: wiki/index.md ===
[full updated index preserving existing entries]
=== END FILE ===

Write both files now."""

        try:
            response = ask(prompt)
            parse_and_write(response, name)
            index = truncate(read_file(INDEX), 3000)

            success.append(name)
            processed += 1

        except Exception as e:
            failed.append((name, str(e)))

            print(f"\n❌ Failed: {name}")
            print(e)

            continue

    print("\n" + "=" * 60)
    print("INGEST COMPLETE")
    print("=" * 60)

    print(f"Successful : {len(success)}")
    print(f"Failed     : {len(failed)}")
    print(f"Processed  : {processed}")

    if failed:
        print("\nFailed files:")
        for file, err in failed:
            print(f" • {file}")

# =============================================================================
#  OPERATION: QUERY
#  Ask your knowledge base a question
# =============================================================================

def op_query(question):
    print("\n" + "=" * 60)
    print("  QUERY — searching your knowledge base")
    print("=" * 60)

    schema = read_file(SCHEMA)
    index  = truncate(read_file(INDEX), 5000)
    context = retrieval_engine.build_context(
    question,
    top_n=5
    )   

    print(f"\n  Question: {question}\n")

    prompt = f"""
    You are a knowledgeable assistant with access to my personal knowledge base.

    Follow these rules:

    {schema}

    ============================================================
    RELEVANT KNOWLEDGE
    ============================================================

    {context}

    ============================================================
    WIKI INDEX (catalog)
    ============================================================

    {index}

    ============================================================
    QUESTION
    ============================================================

    {question}

    Instructions:

    1. Use the retrieved knowledge as your PRIMARY source.

    2. If the retrieved knowledge completely answers the question,
    do not invent additional information.

    3. If the retrieved knowledge is incomplete,
    you may use your own general knowledge,
    but clearly distinguish it from what came from the knowledge base.

    4. Cite relevant notes using
    [source: page-title].

    5. If the vault lacks sufficient information,
    say so and suggest what information would make future answers better.

    Answer clearly and concisely.
    """

    ask(prompt)


# =============================================================================
#  OPERATION: LINT
#  Weekly health check — finds problems in the wiki
# =============================================================================

def op_lint():
    print("\n" + "=" * 60)
    print("  LINT — running weekly wiki health check")
    print("=" * 60)

    schema     = read_file(SCHEMA)
    wiki_files = glob.glob(os.path.join(WIKI, "**/*.md"), recursive=True)

    # Sample up to 30 files (stays within context window)
    sample = wiki_files[:30]
    content = ""
    for fp in sample:
        rel = os.path.relpath(fp, VAULT_PATH)
        content += f"\n\n=== {rel} ===\n" + truncate(read_file(fp), 800)

    print(f"\n  Scanning {len(wiki_files)} wiki files (sampling {len(sample)} for context)...")

    prompt = f"""You are a wiki health auditor. Follow these rules:
{schema}

---
WIKI CONTENT SAMPLE ({len(sample)} files):
{content}

---
TASK — LINT OPERATION:

Carefully read all the wiki content above. Find these problems:
1. CONTRADICTIONS — two pages that say opposite things about the same topic
2. ORPHAN PAGES — pages that no other page links to (check for [[wiki-links]])
3. MISSING PAGES — concepts mentioned in 3+ pages but with no dedicated page
4. OUTDATED CLAIMS — information a newer page contradicts or supersedes
5. ISOLATED PAGES — pages with no outbound [[wiki-links]] to other pages

Write a complete health report. Be specific — name the actual files.

=== FILE: wiki/lint-report.md ===
---
date: {today()[:10]}
---

# Wiki Health Report — {today()[:10]}

## Critical Issues
[contradictions and major problems — fix these first]

## Medium Issues
[orphan pages, missing concept pages]

## Minor Issues
[isolated pages, style inconsistencies]

## Top 3 Things To Fix First
1. [most important fix]
2. [second most important]
3. [third most important]

## Stats
- Files scanned: {len(sample)}
- Total wiki files: {len(wiki_files)}
=== END FILE ==="""

    response = ask(prompt)
    parse_and_write(response, "_lint_")


# =============================================================================
#  OPERATION: MIRROR
#  Monthly thinking pattern analysis
# =============================================================================

def op_mirror():
    print("\n" + "=" * 60)
    print("  THINKING MIRROR — analyzing your thinking patterns")
    print("=" * 60)

    schema     = read_file(SCHEMA)
    wiki_files = glob.glob(os.path.join(WIKI, "**/*.md"), recursive=True)

    sample = wiki_files[:25]
    content = ""
    for fp in sample:
        rel = os.path.relpath(fp, VAULT_PATH)
        content += f"\n\n=== {rel} ===\n" + truncate(read_file(fp), 600)

    print(f"\n  Reading {len(sample)} wiki files for pattern analysis...")

    prompt = f"""You are a candid personal thinking analyst.
Follow these rules:
{schema}

---
WIKI CONTENT ({len(sample)} files):
{content}

---
TASK — THINKING MIRROR OPERATION:

Read all content above. Analyze the thinking patterns across everything written.
Be specific and honest. Cite the actual wiki page names as evidence.
This is for self-understanding — do not flatter, do not soften hard observations.

Find and report on:
1. RECURRING BELIEFS — ideas that appear in 3+ pages (what does this person keep coming back to?)
2. HIDDEN ASSUMPTIONS — things treated as true without being examined
3. CONTRADICTIONS — places where the person disagrees with themselves across topics
4. OBSESSIONS — topics they return to most frequently
5. STRONGEST MENTAL MODELS — frameworks they use to think about problems
6. BLIND SPOTS — what is conspicuously absent that someone with these interests should care about?

=== FILE: wiki/thinking-mirror.md ===
---
date: {today()[:10]}
---

# Thinking Mirror — {today()[:10]}

## Recurring Beliefs
[specific beliefs with page citations]

## Hidden Assumptions
[assumptions the writing relies on but never questions]

## Self-Contradictions
[places where different pages disagree with each other]

## What You Keep Coming Back To
[most frequent topics and why they might matter]

## Your Strongest Mental Models
[frameworks that appear across multiple pages]

## Blind Spots
[what is missing that should be here]

## One Honest Observation
[the single most useful thing to notice about this person's thinking]
=== END FILE ==="""

    response = ask(prompt)
    parse_and_write(response, "_mirror_")


# =============================================================================
#  OPERATION: DIGEST
#  Morning summary of tasks, recent activity, and wiki health
# =============================================================================

def op_digest():
    print("\n" + "=" * 60)
    print(f"  MORNING DIGEST — {today()}")
    print("=" * 60)

    tracker  = truncate(read_file(os.path.join(WIKI, "action-tracker.md")), 2000)
    log      = read_file(LOG)
    lint     = truncate(read_file(os.path.join(WIKI, "lint-report.md")), 1000)

    # --- Open tasks ---
    if tracker:
        print("\n  [ OPEN TASKS ]")
        task_prompt = (
            f"From this action tracker, list only tasks that are due today or overdue. "
            f"Format as a simple numbered list. Be brief — one line per task.\n\n{tracker}"
        )
        ask(task_prompt)
    else:
        print("\n  [ OPEN TASKS ] — no action-tracker.md found yet")

    # --- Recent ingests (last 5, no AI needed) ---
    print("\n  [ RECENT INGESTS ]")
    recent = [l.strip() for l in log.split("\n") if "| source:" in l][-5:]
    if recent:
        for line in recent:
            print(f"    • {line.split('| source:')[-1].strip()}")
    else:
        print("    (no ingests logged yet)")

    # --- Wiki health summary ---
    if lint:
        print("\n  [ WIKI HEALTH — top issues ]")
        lint_prompt = (
            f"From this wiki health report, list the top 3 issues in one short line each. "
            f"Start each with a bullet point.\n\n{lint}"
        )
        ask(lint_prompt)
    else:
        print("\n  [ WIKI HEALTH ] — no lint-report.md yet (run: python3 brain.py lint)")

    print()


# =============================================================================
#  OPERATION: DECISION
#  Decision brief built entirely from your own past history
# =============================================================================

def op_decision(topic):
    print("\n" + "=" * 60)
    print("  DECISION ENGINE — building brief from your history")
    print("=" * 60)

    schema    = read_file(SCHEMA)
    dlog      = truncate(read_file(os.path.join(WIKI, "decision-log.md")), 3000)
    index     = truncate(read_file(INDEX), 2000)
    slug      = topic[:40].replace(" ", "_").replace("/", "-")

    print(f"\n  Decision: {topic}\n")

    prompt = f"""You are a decision analyst. Your only job is to use this person's
own history and knowledge — no outside advice, no generic frameworks.
Follow these rules:
{schema}

---
PAST DECISIONS LOG:
{dlog if dlog else "(no decision-log.md yet — will build from wiki context instead)"}

---
WIKI INDEX:
{index}

---
DECISION TO MAKE: {topic}

Using ONLY what is in the person's own history and wiki above, write a decision brief.
If there is no past history on this topic, say so honestly.

=== FILE: wiki/decisions/{slug}.md ===
---
date: {today()[:10]}
decision: {topic}
---

# Decision Brief: {topic}

## What My Own History Says
[what past decisions or beliefs are relevant — cite specific wiki pages or log entries]

## Beliefs I Hold That Apply Here
[from the wiki — what do I already believe about this domain?]

## Where I Have Been Right Before In Similar Situations
[specific past patterns — only if evidence exists]

## Where I Have Been Wrong Before
[honest assessment — only if evidence exists]

## The Question I Might Be Avoiding
[the uncomfortable question at the center of this decision]

## What I Would Tell Myself
[a direct recommendation based only on my own history — not generic advice]
=== END FILE ==="""

    response = ask(prompt)
    parse_and_write(response, "_decision_")


# =============================================================================
#  OPERATION: MOC
#  Create a Map of Content — a high-level topic overview page
# =============================================================================

def op_moc(topic):
    print("\n" + "=" * 60)
    print(f"  MAP OF CONTENT — {topic}")
    print("=" * 60)

    schema = read_file(SCHEMA)
    index  = truncate(read_file(INDEX), 5000)
    slug   = topic.lower().replace(" ", "-").replace("/", "-")

    print(f"\n  Building overview page for: {topic}\n")

    prompt = f"""You are a knowledge cartographer. Your job is to map out
everything in a wiki related to a specific topic.
Follow these rules:
{schema}

---
WIKI INDEX:
{index}

---
TOPIC: {topic}

Create a comprehensive Map of Content for this topic.
Link every related wiki page using [[wiki-links]].

=== FILE: moc/{slug}-moc.md ===
---
topic: {topic}
date_created: {today()[:10]}
type: moc
---

# {topic} — Map of Content

## Overview
[2-paragraph overview of everything the wiki knows about this topic]

## Core Pages
[the 3 most important pages on this topic — with [[links]] and one-line descriptions]

## All Related Pages
[every wiki page touching this topic, grouped by sub-theme]
[format: - [[page-name]] — one-line description]

## Knowledge Gaps
[top 3 things missing from the wiki on this topic]

## What To Read Next
[3 specific types of sources to find and ingest to fill the gaps]
=== END FILE ==="""

    response = ask(prompt)
    parse_and_write(response, "_moc_")


# =============================================================================
#  MAIN — command parser and help text
# =============================================================================

COMMANDS = {
    "ingest":   {
        "fn": op_ingest,
        "args": 0,
        "desc": "Process newest uningested file from raw-sources/",
        "example": "python3 brain.py ingest"
    },
    "ingest-all": {
        "fn": op_ingest_all,
        "args": 0,
        "desc": "Process ALL uningested files from raw-sources/",
        "example": "python3 brain.py ingest-all"
    },
    "query":    {
        "fn": op_query,
        "args": 1,
        "desc": "Ask your knowledge base a question",
        "example": 'python3 brain.py query "What do I know about X?"'
    },
    "lint":     {
        "fn": op_lint,
        "args": 0,
        "desc": "Weekly wiki health check (run every Sunday)",
        "example": "python3 brain.py lint"
    },
    "mirror":   {
        "fn": op_mirror,
        "args": 0,
        "desc": "Monthly thinking pattern analysis",
        "example": "python3 brain.py mirror"
    },
    "digest":   {
        "fn": op_digest,
        "args": 0,
        "desc": "Morning summary of tasks, ingests, and wiki health",
        "example": "python3 brain.py digest"
    },
    "decision": {
        "fn": op_decision,
        "args": 1,
        "desc": "Build a decision brief from your own history",
        "example": 'python3 brain.py decision "Should I take this job?"'
    },
    "moc":      {
        "fn": op_moc,
        "args": 1,
        "desc": "Create a Map of Content for a topic",
        "example": 'python3 brain.py moc "machine learning"'
    },
}


def print_help():
    print("\n" + "=" * 60)
    print("  brain.py — Local AI Second Brain")
    print(f"  Vault:  {VAULT_PATH}")
    print(f"  Model:  {MODEL}")
    print("=" * 60)
    print("\n  Commands:\n")
    for cmd, info in COMMANDS.items():
        print(f"  {cmd:<12} {info['desc']}")
        print(f"  {'':12} Example: {info['example']}\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print_help()
        return

    cmd  = sys.argv[1]
    info = COMMANDS[cmd]

    if info["args"] == 1 and len(sys.argv) < 3:
        print(f"\n  ERROR: '{cmd}' needs an argument.")
        print(f"  Example: {info['example']}")
        return

    arg = " ".join(sys.argv[2:]) if info["args"] == 1 else None

    if arg:
        info["fn"](arg)
    else:
        info["fn"]()


if __name__ == "__main__":
    main()
