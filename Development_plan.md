# Development Plan (Multi-Week)

## Week 1 — Product Definition & Foundation

**Goals**
- Establish product requirements, success metrics, and user journeys.
- Create technical architecture and foundational project setup.

**Deliverables**
- Product brief with MVP scope (Memory Engine, Contradiction Detector, Daily/Weekly Interrogation).
- User stories and acceptance criteria for each MVP feature.
- System architecture diagram and data flow sketch.
- Project scaffolding (repo structure, linting/formatting, CI basics).
- Initial API/service decisions (in-house vs external providers).

**Suggested Activities**
- Define primary personas (e.g., busy professional, founder, student).
- Draft MVP user flows: capture → store → challenge → review.
- Decide data storage (e.g., Postgres) and vector store (e.g., pgvector, Pinecone, Weaviate).
- Choose LLM provider and embedding model for the Memory Engine.

---

## Week 2 — Memory Engine (Core Data + Retrieval)

**Goals**
- Build the core data model and basic capture/retrieval workflows.
- Ensure data is ready for embeddings and analysis.

**Deliverables**
- Data schema for goals, notes, plans, and metadata.
- CRUD APIs for capturing and retrieving items.
- Embedding pipeline for all new items.
- Basic retrieval API (keyword + semantic).

**Suggested Activities**
- Define “importance” metadata and timestamping rules.
- Add background job for embedding ingestion.
- Implement a simple search UI or CLI for validation.

---

## Week 3 — Contradiction Detector (Insights & Alerts)

**Goals**
- Detect inconsistencies and contradictions across goals, notes, and actions.
- Provide feedback with explanation and confidence levels.

**Deliverables**
- Contradiction detection logic (rules + model-assisted).
- API endpoint for contradiction analysis.
- Stored contradiction history with timestamps.

**Suggested Activities**
- Start with rule-based checks (goal vs action mismatch, abandoned ideas).
- Add model-assisted classification for ambiguous contradictions.
- Provide “why it’s a contradiction” explanation strings.

---

## Week 4 — Daily / Weekly Interrogation Experience

**Goals**
- Deliver AI-generated prompts to challenge the user.
- Provide a scheduled routine for reflection.

**Deliverables**
- API for daily/weekly prompt generation.
- Prompt templates (3 uncomfortable questions, 1 forced choice, 1 finish-or-delete).
- Scheduling mechanism (cron/worker).
- Simple UI or notification channel.

**Suggested Activities**
- Build prompt templates with few-shot examples.
- Add user response capture and storage.
- Provide follow-up prompts based on previous answers.

---

## Week 5 — Integration, Polishing, and MVP Launch

**Goals**
- Connect all features into a cohesive flow.
- Improve UX and reliability.

**Deliverables**
- End-to-end flow: capture → detect contradictions → interrogate → follow-up.
- Basic analytics and logging.
- User onboarding guide.
- MVP launch checklist.

**Suggested Activities**
- Run internal tests on different personas.
- Tune contradiction and interrogation prompts.
- Prepare deployment (Docker, staging environment, minimal monitoring).

---

## Optional APIs & Services

**LLM Providers**
- OpenAI, Anthropic, or Azure OpenAI for reasoning and interrogation prompts.

**Embeddings**
- OpenAI embeddings, Cohere, or local models with a vector database.

**Vector Storage**
- pgvector (Postgres), Pinecone, Weaviate.

**Scheduling/Notifications**
- Cron jobs, serverless functions, or webhook-based reminders.
