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

def read_page(path):
    """
    Read a wiki page.
    """

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()
    
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

        results.append({

            "title": name,

            "score": score,

            "path": path,

            "content": read_page(path)

        })

    return results

if __name__ == "__main__":

    page = os.path.join(

        WIKI_DIR,

        "AI_Knowledge_Base_Built_on_Karpathy’s_LLM_Wiki_Method_summary.md"

    )

    pages = retrieve_similar_pages(page)

    for p in pages:

        print()

        print("=" * 60)

        print(p["title"])

        print(p["score"])

        print()

        print(p["content"][:300])

        print("...")