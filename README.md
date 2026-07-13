# 🧠 Second Brain

> An AI-powered personal knowledge management system that transforms scattered information into connected, actionable knowledge.

---

## The Problem

We live in an age of information abundance.

Every day we save articles, bookmark websites, star GitHub repositories, highlight books, and take notes. We tell ourselves we'll come back to them later.

Most of the time, we never do.

Over time, our knowledge becomes scattered across note-taking apps, browsers, documents, chats, and code repositories. We don't have an information shortage—we have an information management problem.

Traditional note-taking applications are great at storing information, but they don't understand it.

Modern Large Language Models (LLMs) can answer questions remarkably well, but they don't naturally maintain a persistent, structured understanding of *your* knowledge.

There is a gap between storage and understanding.

Second Brain aims to bridge that gap.

---

# What is Second Brain?

Second Brain is an AI-powered knowledge management system that combines the permanence of a note-taking application with the reasoning capabilities of modern language models.

Instead of simply storing notes, it continuously works with your knowledge.

The long-term vision is an AI that can:

* Understand your personal knowledge base
* Connect related ideas automatically
* Organize information intelligently
* Update existing notes instead of creating duplicates
* Remember what you've learned over time
* Help retrieve knowledge through natural language

Think of it as:

> **Obsidian + AI + Long-Term Memory**

---

# Current Features

The project is currently in its early development stages.

### ✅ Working

* Reads an Obsidian knowledge vault
* Understands existing context
* Updates notes with new information
* Automatically organizes knowledge
* Local LLM support
* End-to-end workflow

---

# Planned Features

The roadmap includes:

* Semantic Search
* Knowledge Graph Generation
* Automatic Note Linking
* Intelligent Tagging
* Daily Knowledge Summaries
* Research Assistant
* Learning Companion
* Retrieval-Augmented Generation (RAG)
* Long-term Memory
* Multi-file Context Understanding
* Plugin Architecture
* Local-first Design

---

# Architecture (Current)

```text
                User
                  │
                  ▼
             brain.py
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
 Local LLM              Obsidian Vault
      │                       │
      └───────────┬───────────┘
                  ▼
        Updated Knowledge Base
```

---

# Tech Stack

* Python
* Local LLMs
* Obsidian Markdown Vault
* Markdown Processing
* Prompt Engineering

---

# Why Local?

Second Brain is designed with privacy in mind.

Your notes represent your personal knowledge and shouldn't have to leave your machine.

Running everything locally allows for:

* Privacy
* Offline usage
* Lower long-term cost
* Full control over your data

---

# Project Status

🚧 Early Development

The current version runs entirely from the terminal and focuses on building a reliable core workflow before adding more advanced capabilities.

The foundation is working.

Now it's time to make it smarter.

---

# Vision

Imagine an AI that doesn't just answer your questions.

Imagine one that remembers everything you've learned over the past five years, understands how those ideas relate to one another, and helps you build upon them.

That's the goal of Second Brain.

---

# Contributing

The project is still evolving, and ideas, feedback, and discussions are always welcome.

If you have suggestions or would like to contribute, feel free to open an issue or submit a pull request.

---

# License

MIT License
