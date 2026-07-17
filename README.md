# Second Brain

> A local AI-powered knowledge operating system that transforms raw information into an interconnected, searchable knowledge base using semantic search and Retrieval-Augmented Generation (RAG).

<img width="1590" height="1059" alt="a7fefb722b92c129d277510f83623169ceaac83b" src="https://github.com/user-attachments/assets/fed2d4cf-265f-4f81-a390-c175099b2697" />

## Overview

Second Brain is a fully local knowledge management system designed to solve a common problem:

We save hundreds of articles, videos, notes, and ideas—but almost never revisit them.

Instead of acting as a storage system, Second Brain continuously converts raw information into structured knowledge that compounds over time.

It automatically:

- Ingests articles and notes
- Extracts structured knowledge using an LLM
- Builds a semantic vector index
- Retrieves relevant knowledge using embeddings
- Answers questions grounded in your own knowledge base

Unlike traditional note-taking applications, Second Brain is designed to become an intelligent knowledge layer rather than another folder full of notes.

---

# Features

## Knowledge Ingestion

- Automatic processing of new articles
- Converts raw documents into structured wiki pages
- Generates summaries and key concepts
- Updates vault automatically

## Semantic Search

Instead of keyword matching, the system searches by meaning.

```
User Question
      ↓
Sentence Embedding
      ↓
Cosine Similarity
      ↓
Top-k Relevant Notes
```
<img width="982" height="486" alt="image" src="https://github.com/user-attachments/assets/81cc8989-e140-46d2-bdf6-4cc4df985b7b" />

## Retrieval-Augmented Generation (RAG)

Retrieved knowledge is injected into the LLM prompt before answering.

```
Question
      ↓
Semantic Retrieval
      ↓
Relevant Knowledge
      ↓
LLM
      ↓
Grounded Response
```
<img width="432" height="585" alt="image" src="https://github.com/user-attachments/assets/aa5ba0d2-8272-49b4-81af-daaa4d6d2605" />


## Automatic Embeddings

Every generated wiki page automatically receives a semantic embedding.

Embeddings stay synchronized with the knowledge base during ingestion.

## UUID-based Metadata Registry

Pages are tracked using permanent UUIDs rather than filenames.

Metadata includes:

- UUID
- Title
- Path
- Embedding location
- Timestamps
- Embedding model

This prevents broken references when notes are renamed.

## Modular Architecture

Responsibilities are separated into independent modules:

- Ingestion
- Embeddings
- Retrieval
- Knowledge generation

---

# Architecture

```
                    Raw Sources
               (Articles / Notes)
                       │
                       ▼
                 brain.py ingest
                       │
                       ▼
             Qwen2.5 (Knowledge Extraction)
                       │
                       ▼
               Structured Wiki Pages
                       │
                       ▼
             embedding_engine.py
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 Embeddings (.npy)             Metadata Registry
        │                             │
        └──────────────┬──────────────┘
                       ▼
             retrieval_engine.py
                       │
                       ▼
              Semantic Search
                       │
                       ▼
               Context Builder
                       │
                       ▼
               Qwen2.5 via Ollama
                       │
                       ▼
             Grounded AI Response
```

---

# Retrieval Pipeline

```
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Cosine Similarity Search
      │
      ▼
Top-k Retrieval
      │
      ▼
Knowledge Extraction
      │
      ▼
Prompt Construction
      │
      ▼
LLM Response
```

---

# Project Structure

```
second-brain/

├── brain.py
├── embedding_engine.py
├── retrieval_engine.py
├── CLAUDE.md
│
├── raw-sources/
│
├── wiki/
│
├── moc/
│
└── .brain/
    ├── embeddings/
    └── metadata/
```

---

# Tech Stack

### Language

- Python

### Local LLM

- Qwen2.5:7B
- Ollama

### Embedding Model

- sentence-transformers
- all-MiniLM-L6-v2

### Vector Search

- NumPy
- Cosine Similarity

### Knowledge Storage

- Markdown
- UUID metadata registry
- Local embedding files (.npy)

---

# Commands

## Ingest newest file

```bash
python brain.py ingest
```

## Ingest all files

```bash
python brain.py ingest-all
```

## Query the knowledge base

```bash
python brain.py query "How can AI improve knowledge management?"
```

## Generate morning digest

```bash
python brain.py digest
```

## Weekly vault health check

```bash
python brain.py lint
```

## Monthly reflection

```bash
python brain.py mirror
```

## Decision brief

```bash
python brain.py decision
```

## Create Map of Content

```bash
python brain.py moc
```

---

# Technical Details

## Knowledge Representation

The system converts raw documents into structured wiki pages containing:

- Summary
- Key Concepts
- Relationships
- Source Information

The wiki serves as the canonical knowledge representation.

---

## Embedding System

Each wiki page receives a semantic embedding generated using SentenceTransformers.

Embeddings are stored independently from notes and linked through a UUID-based metadata registry.

This allows:

- File renaming
- File movement
- Duplicate titles

without invalidating embeddings.

---

## Metadata Registry

Each document stores metadata similar to:

```json
{
  "id": "...",
  "title": "...",
  "path": "...",
  "embedding": "...",
  "created": "...",
  "updated": "...",
  "model": "all-MiniLM-L6-v2"
}
```

---

## Retrieval

Retrieval consists of:

1. Embed user query
2. Compare with stored embeddings
3. Rank using cosine similarity
4. Retrieve top-k notes
5. Extract summaries and concepts
6. Build RAG context
7. Generate grounded answer

---

# Current Capabilities

- ✅ Automatic knowledge ingestion
- ✅ Structured wiki generation
- ✅ Local embeddings
- ✅ Metadata registry
- ✅ Semantic search
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Grounded question answering
- ✅ Local-first architecture

---

# Roadmap

## Retrieval

- [ ] Chunk-level retrieval
- [ ] Hybrid search (semantic + keyword)
- [ ] Cross-encoder reranking
- [ ] Incremental embedding updates

## Knowledge

- [ ] Automatic semantic backlinks
- [ ] Entity extraction
- [ ] Knowledge graph generation
- [ ] Relationship discovery

## Intelligence

- [ ] Research mode
- [ ] Multi-document synthesis
- [ ] Autonomous knowledge maintenance
- [ ] Self-improving knowledge graph

---

# Why?

Modern note-taking applications optimize for storing information.

Second Brain optimizes for **using** information.

Instead of remembering where something was saved, you simply ask a question and receive an answer grounded in your own accumulated knowledge.

The goal is to build a personal knowledge system that compounds over time—turning information into an interconnected, searchable, and continuously growing knowledge base.

---

## License

MIT License
