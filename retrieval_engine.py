"""
retrieval_engine.py

Semantic retrieval layer.

Responsibilities

- Search embeddings
- Load wiki pages
- Return relevant knowledge

No Ollama.
No prompting.
"""

import os

import numpy as np

import embedding_engine

VAULT_PATH = os.path.dirname(
    os.path.abspath(__file__)
)

WIKI_DIR = os.path.join(
    VAULT_PATH,
    "wiki"
)
# =============================================================================
# PAGE PARSING
# =============================================================================
def extract_knowledge(path):
    """
    Extract only the useful information from a wiki page.
    """

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()
    title = ""

    for line in text.splitlines():

        if line.startswith("# "):

            title = line[2:].strip()

            break
    summary = ""

    if "## Summary" in text:

        part = text.split("## Summary", 1)[1]

        if "##" in part:

            summary = part.split("##", 1)[0]

        else:

            summary = part

    summary = summary.strip()
    concepts = []

    if "## Key Concepts" in text:

        part = text.split("## Key Concepts", 1)[1]

        if "##" in part:

            part = part.split("##", 1)[0]

        for line in part.splitlines():

            line = line.strip()

            if line.startswith("-"):

                concepts.append(
                    line[1:].strip()
                )
    return {

        "title": title,

        "summary": summary,

        "key_concepts": concepts

    }
    
def retrieve_similar_pages(
    wiki_file,
    top_n=5
):
    """
    Return the contents of the most similar pages.
    """

    similar = embedding_engine.find_similar_pages(
        wiki_file,
        top_n
    )

    results = []

    for name, score in similar:

        path = os.path.join(
            WIKI_DIR,
            name
        )

        if not os.path.exists(path):
            continue

        knowledge = extract_knowledge(path)

        results.append({

            "title": knowledge["title"],

            "score": score,

            "summary": knowledge["summary"],

            "key_concepts": knowledge["key_concepts"],

            "path": path

        })

    return results
# =============================================================================
# PUBLIC API
# =============================================================================
def build_context(query, top_n=5):
    """
    Build a formatted context string for the LLM.
    """

    pages = retrieve_context(query, top_n)

    if not pages:
        return "No relevant knowledge found."

    context = []

    for page in pages:

        concepts = "\n".join(
            f"- {c}" for c in page["key_concepts"]
        )

        section = f"""
============================================================
SOURCE: {page['title']}
Similarity: {page['score']:.3f}

SUMMARY
{page['summary']}

KEY CONCEPTS
{concepts}
"""

        context.append(section)

    return "\n".join(context)

def retrieve_context(query, top_n=5):
    """
    Retrieve the most relevant knowledge for a text query.
    """

    # Convert the query into an embedding
    query_embedding = embedding_engine.embed_text(query)

    results = []

    metadata = embedding_engine.load_metadata()

    for wiki_path, record in metadata.items():

        embedding_path = os.path.join(
            embedding_engine.EMBED_DIR,
            record["embedding"]
        )

        if not os.path.exists(embedding_path):
            continue

        candidate_embedding = np.load(embedding_path)

        score = embedding_engine.cosine_similarity(
            query_embedding,
            candidate_embedding
        )

        full_path = os.path.join(
            embedding_engine.VAULT_PATH,
            wiki_path
        )

        if not os.path.exists(full_path):
            continue

        knowledge = extract_knowledge(full_path)

        results.append({

            "title": knowledge["title"],

            "score": score,

            "summary": knowledge["summary"],

            "key_concepts": knowledge["key_concepts"],

            "path": full_path

        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_n]

if __name__ == "__main__":

    results = retrieve_context(
        "How can AI improve knowledge management?"
    )

    for page in results:

        print("=" * 60)

        print(page["title"])

        print(f"Score: {page['score']:.3f}")

        print()

        print("Summary:")
        print(page["summary"])

        print()

        print("Key Concepts:")

        for concept in page["key_concepts"]:
            print("-", concept)

        print()

