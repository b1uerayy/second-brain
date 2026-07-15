"""
embedding_engine.py

Handles everything related to semantic embeddings.

Responsibilities:
- Load embedding model
- Create embeddings
- Save embeddings
- Load embeddings
- Compute similarity

No Ollama.
No prompts.
No CLI.
"""

import os
import numpy as np
from sentence_transformers import SentenceTransformer

# =============================================================================
# PATHS
# =============================================================================

VAULT_PATH = os.path.dirname(os.path.abspath(__file__))

BRAIN_DIR = os.path.join(VAULT_PATH, ".brain")
EMBED_DIR = os.path.join(BRAIN_DIR, "embeddings")

os.makedirs(EMBED_DIR, exist_ok=True)

# =============================================================================
# MODEL
# =============================================================================

print("Loading embedding model...")

EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")

EMBED_CACHE = {}

def load_all_embeddings():
    """
    Load every embedding into memory once.
    """

    global EMBED_CACHE

    if EMBED_CACHE:
        return EMBED_CACHE

    for file in os.listdir(EMBED_DIR):

        if file.endswith(".npy"):

            EMBED_CACHE[file] = np.load(
                os.path.join(EMBED_DIR, file)
            )

    return EMBED_CACHE



# =============================================================================
# EMBEDDING
# =============================================================================

def embed_text(text):
    """
    Convert text into a semantic embedding.

    Returns:
        numpy.ndarray
    """

    return EMBEDDER.encode(
        text,
        normalize_embeddings=True
    )

# =============================================================================
# PATH HELPERS
# =============================================================================

def embedding_path(wiki_file):
    """
    Convert a wiki filename into an embedding filename.

    Example:

    wiki/AI.md

    becomes

    .brain/embeddings/AI.npy
    """

    filename = os.path.basename(wiki_file)

    filename = os.path.splitext(filename)[0]

    return os.path.join(
        EMBED_DIR,
        filename + ".npy"
    )

def wiki_from_embedding(embedding_file):
    """
    Convert an embedding filename back into a wiki filename.

    AI.npy

    becomes

    AI.md
    """

    name = os.path.splitext(
        os.path.basename(embedding_file)
    )[0]

    return name + ".md"

# =============================================================================
# STORAGE
# =============================================================================

def save_embedding(wiki_file, embedding):
    """
    Save one embedding to disk.
    """

    np.save(
        embedding_path(wiki_file),
        embedding
    )

# =============================================================================
# WIKI PAGE READER
# =============================================================================

def read_wiki_page(wiki_file):
    """
    Read only the semantically meaningful parts of a wiki page.

    We intentionally ignore:
    - YAML frontmatter
    - Connections
    - Quotes
    """

    with open(wiki_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = []

    in_frontmatter = False
    current_section = None

    useful_sections = {
        "summary",
        "key concepts"
    }

    for line in lines:

        stripped = line.strip()

        # -----------------------------
        # YAML frontmatter
        # -----------------------------
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue

        if in_frontmatter:
            continue

        # -----------------------------
        # Keep page title
        # -----------------------------
        if stripped.startswith("# "):
            cleaned.append(stripped)
            continue

        # -----------------------------
        # Detect section headings
        # -----------------------------
        if stripped.startswith("## "):
            current_section = stripped[3:].lower()

            if current_section in useful_sections:
                cleaned.append(stripped)

            continue

        # -----------------------------
        # Keep only useful sections
        # -----------------------------
        if current_section in useful_sections:
            cleaned.append(line)

    return "\n".join(cleaned)

# =============================================================================
# WIKI PAGE EMBEDDING
# =============================================================================

def embed_wiki_page(wiki_file):
    """
    Read a wiki page, generate its embedding,
    save it, and return the vector.
    """

    text = read_wiki_page(wiki_file)

    embedding = embed_text(text)

    save_embedding(wiki_file, embedding)

    return embedding

# =============================================================================
# INDEX ALL WIKI PAGES
# =============================================================================

def embed_all_wiki_pages():
    """
    Generate embeddings for every wiki page.
    """

    wiki_dir = os.path.join(VAULT_PATH, "wiki")

    files = [
    f
    for f in os.listdir(wiki_dir)
    if (
        f.endswith(".md")
        and f not in ("index.md", "log.md")
    )
   ]

    if not files:
        print("No wiki pages found.")
        return

    print(f"\nEmbedding {len(files)} wiki pages...\n")

    for i, file in enumerate(files, start=1):

        path = os.path.join(wiki_dir, file)

        if load_embedding(path) is None:

            embed_wiki_page(path)

            print(f"[{i}/{len(files)}] Embedded: {file}")

        else:

            print(f"[{i}/{len(files)}] Skipped:  {file}")

    print("\nFinished embedding wiki.")

def rebuild_embeddings():
    """
    Delete all embeddings and regenerate them.
    """

    embeddings = load_all_embeddings()

    for file, candidate_vec in embeddings.items():

        if file.endswith(".npy"):

            os.remove(os.path.join(EMBED_DIR, file))

    print("Old embeddings deleted.\n")

    embed_all_wiki_pages()


def load_embedding(wiki_file):
    """
    Load one embedding from disk.
    """

    path = embedding_path(wiki_file)

    if not os.path.exists(path):
        return None

    return np.load(path)

# =============================================================================
# SIMILARITY
# =============================================================================

def cosine_similarity(vec1, vec2):
    """
    Compare two embeddings.

    Returns:

        1.0 = identical

        0.0 = unrelated

       -1.0 = opposite
    """

    return float(np.dot(vec1, vec2))

# =============================================================================
# FIND SIMILAR PAGES
# =============================================================================

def find_similar_pages(wiki_file, top_n=5):
    """
    Return the most semantically similar wiki pages.

    Returns:

        [
            ("Knowledge.md", 0.91),
            ("AI.md", 0.88)
        ]
    """

    target = load_embedding(wiki_file)

    if target is None:
        print("No embedding exists for this page.")
        return []

    results = []

    for file in os.listdir(EMBED_DIR):

        if not file.endswith(".npy"):
            continue

        candidate = os.path.join(
            EMBED_DIR,
            file
        )

        candidate_vec = np.load(candidate)

        score = cosine_similarity(
            target,
            candidate_vec
        )

        wiki_name = wiki_from_embedding(file)

        # Don't compare page to itself
        if wiki_name == os.path.basename(wiki_file):
            continue

        results.append(
            (
                wiki_name,
                score
            )
        )

    results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return results[:top_n]

# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":

    embed_all_wiki_pages()

    print("\n")

    page = os.path.join(
        VAULT_PATH,
        "wiki",
        "AI_Knowledge_Base_Built_on_Karpathy’s_LLM_Wiki_Method_summary.md"
    )

    similar = find_similar_pages(page)

    print("Most similar pages:\n")

    for name, score in similar:

        print(f"{score:.3f}   {name}")