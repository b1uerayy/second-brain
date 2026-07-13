---
title: "Building AI Strategy on Sand"
source: "https://substack.com/home/post/p-204069373"
author:
  - "[[Veronika Heimsbakk]]"
published: 2026-06-29
created: 2026-07-13
description: "Why concept management and knowledge representation decides whether your AI gives the right answers"
tags:
  - "clippings"
---
![](https://substackcdn.com/image/fetch/$s_!a5pk!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9eadcc6a-5572-4053-8e0b-2c85790db55e_4167x1592.png)

Communication (SHACL for the Practitioner, Heimsbakk)

This article is an English summary of a half-day course I made on commission for Brønnøysundregistrene titled *“AI for Leaders”*, and was thrown in a shorted down variant at a *[webinar hosted by The Norwegian Digitalisation Agency](https://www.digdir.no/datadeling/fagleg-arena-datadeling-og-informasjonsforvaltning/8056)*. It adresses what’s important to embrace in an organisation’s AI strategy from a point of view that Digital Norway [^1] does not teach (yet).

---

Almost every organisation I talk to wants to “do something with AI”. The focus around word meanings, however, is not that high up the agenda for many. The single biggest determinant of whether a language model gives your users correct answers isn’t what model you pick, but whether the data behind it contain clear, consistent, well-defined concepts. Get your concepts wrong, and you get answers that sound right, but are not. This is an expensive failure which is hard to detect.

This piece, as mentioned, is targeted towards leaders and managers, not engineers. There is no need to write a single line of code to make a decision that matters in this case. But you do need to understand why concept management is the foundation your AI is built on, and why treating it as an afterthought means you’ll be building on sand.

## AI is more than large language models

![](https://substackcdn.com/image/fetch/$s_!ZtAZ!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3267f07c-187b-4260-98e1-784ac2e33f2b_1920x1080.png)

The AI umbrella, made by the author.

It’s worth remembering that “AI” is a big umbrella. Large language models are the part everyone is excited about right now, but you’ll also find *perception*, *learning*, *reasoning*, *logical deduction* and ***knowledge representation*** among the AI disciplines.

Knowledge representation means describing reality; concepts, the relationships between them, and the rules that govern them, in a form that both humans and machines can understand and use. A language model is brilliant with text, but has no inherent grasp of *meaning*. It finds patterns in language and depends on consistent terminology to do so. When the underlying sources are vague or contradictory, the model produces plausible nonsense. When they are precise and structured, the model can ground its answers in something verifiable.

## From data to insight

A useful way to think about this is the climb from data to insight.

**Data** is raw values, add context and data becomes **information**. Structure that information into facts and relationships and you get **knowledge**. Apply judgement and experience on top and you reach **insight**.

Language models operate on text data. They need *structured knowledge* to give precise answers. The better you organise the path from data to knowledge, the better the insight you AI tools can offer.

## Concept, term, definition

Three things that does most of the work.

- A **concept** is the idea of a thing. A mental construction, not the physical thing itself. (Example: the idea of a furry pet that says “meow”.)
- A **term** is the word (or words) we use for that concept. (Example: “Cat”.)
- A **definition** constraints how the term may be interpreted, reducing ambiguity. (Example: A cat is a small, domesticated carnivorous mammal (Felis catus) known for its soft fur, agility, and companionship.)
- And **context** describes how a concepts relates to other concepts.

Let’s take an example from Brønnøysundregistrene (The Brønnøysund Register Centre). Words like “entity”, “enterprise”, and “organisation number” is all over. Their meaning is maybe not the most difficult thing here, but are the concepts used *consistently across every single register and system*? For many organisations, they are not. The same word means slightly different things in different places and context, and one does not notice until a machine tries to reason across all of them at once.

For my course at Brønnøysund, I used the hunter registry as an example (close to heart ❤️). Let’s take the concept of “hunter”. The lazy definition is “someone who hunts”, but the real definition for the hunter registry is “a person registered in the Hunter Registry who has paid the hunting fee for the current hunting year”. Precision! Without this precision, an AI model cannot distinguish a registered, fee-paying hunter from someone who hunts illegally. A definition limits the possible interpretation, making the concept useful.

## Urgency

There are two forces converging to make concept management a board-level concern rather than a librarian’s hobby.

The first is how AI actually reaches your data. There are two dominating patterns;

1. **Retrieval Augmented Generation (RAG)**: the model search your data and use what it finds to compose an answer. So the quality of your data determines the quality of the answer.
2. **Model Context Protocol (MCP)**: connects the model directly to your systems so it can pull structured data in real time.

Both approaches require unambiguous concepts to return correct results.

Ask yourself: what happens when a citizen asks an AI chatbot a question and the model pulls data from sources that use *different terms for the same concept*?

You get confident, contradictory answers — the worst possible outcome for an institution that trades on trust.

The second force is regulation. In the EU, **Interoperable Europe Act** (Regulation 2024/903, in force since 2024) makes interoperability of public-sector systems a binding legal obligation. And interoperability presupposes a shared vocabulary. The **Data Governance Act** pushes public bodies toward publishing standardised metadata. The **AI Act** sets requirements for data quality in training data and decision support. What they all have in common is that they assume that public-sector bodies have their own conceptual house in order.

## The FAIR test

A quick way to audit yourself is the FAIR principles. Data should be **F** indable, **A** ccessible, **I** nteroperable, and **R** eusable. Note that all these aspects depends on concepts. Data is findable when it’s described with standardised terms. It’s accessible when clear definitions make it understandable. It’s interoperable when systems share a common conceptual apparatus. It’s reusable when it’s well enough described to be picked up by an organisation (or AI system) later. Without standardised concepts, data cannot be found, understood, connected or reused, and the whole FAIR model collapses.

## You do not have to invent the wheel

Some good news! This is a solved problem at the standards level. You are not being asked to fund original research.

There are mature, international standards for exactly this work. The W3C’s **SKOS** (Simple Knowledge Organization System) is a standard way to describe what concepts mean with a preferred term, a definition, a unique identifier, the responsible owner, and the relationships to other concepts. The EU’s **Core Vocabularies** (Core Business, Core Person, Core Location, etc.) give shared data models for the public sector and map directly onto the Interoperable Act. **CPSV** (Core Public Service Vocabulary) describes a (life) *event* triggers a *service*, which produces a *result*.

In Norway, we have adapted the European application profiles of these standards —SKOS-AP-NO for concepts, DCAT-AP-NO for dataset descriptions, CPSV-AP-NO for services — built on the same EU vocabularies, and a national data catalogue (data.norge.no) collects concepts across the public sector. When you describe your concepts in SKOS and your services in CPSV, the two fits like a hand in a glove; the concepts give precise semantics, the services give context and process, and an AI system can use both to answer “what do I need in order to do X?” accurately and guide the user through the actual process. The wheel exists! The job is to put it on your own cart.

## What leaders actually need to do

1. First, accept that good concept management is a *precondition* for succeeding with AI, not a parallel project you run if there’s budget left over.
2. Second, use the established standards and tools rather than inventing your own; the EU vocabularies, SKOS, CPSV, DCAT and whatever national profiles apply to you.
3. Third, treat this as a strategic choice requiring organisational ownership. This is not an IT-problem, it is not an information architecture problem either. It’s organisational, and should be anchored in your organisation’s data strategy. The value does not necessarily lie within making things machine-readable, but it is in the process: deciding what your concepts mean, who owns them, and how they relate. RDF [^2] and friends.

So, ***who owns the concepts in your department, and who should?*** If you can’t answer that, you don’t yet have an AI strategy. You have an AI aspiration sitting on sand.

---

#### About the author

![](https://substackcdn.com/image/fetch/$s_!mayx!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2239fd07-e1c7-44a5-9ab2-3e16cf12d14d_520x349.heic)

Ontologist who code in C, Java and Python. Been a knowledge graph practitioner for over a decade, and had numerous talks on the topic around the globe. Knowledge Graph Specialist at Data Treehouse. Author of *[SHACL for the Practitioner](http://shacl.veronahe.no/)* and awarded amongst Norway’s Top 50 Women in Tech 2024.

[^1]: A non-profit organisation that offers courses and trainings on digitalisation, including courses on AI (focused on generative AI).

[^2]: Resource Description Framework, the foundational standard for knowledge representation. Standardised by W3C (1999) with updates; RDF 1.1 (2014), and RDF 1.2 (ongoing).