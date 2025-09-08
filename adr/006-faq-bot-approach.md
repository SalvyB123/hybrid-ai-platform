# ADR-006: FAQ Bot Approach

**Status:** Accepted  
**Date:** 2025-09-08  
**Context:** Week 4 – Foundations (Lean MVP)

---

## 1. Problem

We need a small, reliable **FAQ Bot (V1)** that answers **5–10 curated FAQs** locally.  
When confidence is low, it must **escalate to a human via email**.

Constraints:

-   Solo dev on an M4 MacBook Pro.
-   Keep costs near zero.
-   Ensure stable, fast CI.
-   Must be recruiter-demo friendly.

---

## 2. Decision

Adopt a **minimal retrieval approach without an LLM** for V1:

-   **Source of truth:** `data/faqs.yaml` containing `{id, question, answer, tags?}`.
-   **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (CPU on Mac).
-   **Index:** In-memory matrix with **cosine similarity** via NumPy.
-   **Threshold:** Configurable; default **0.60**.
-   **Handoff:** If `score < threshold`, send an email to a monitored inbox (dev: **MailHog**).
-   **API:** `POST /faq/ask` → returns `{answer, score, source_id}` or `{handoff: true, score, question}`.
-   **Observability:** GDPR-safe logs (request id + outcome, no full PII).

**Rationale:**  
This is the most **cost-effective**, **deterministic**, and **testable** path to a credible recruiter demo, with a clean upgrade path later.

---

## 3. Options considered

| Option                               |  Cost | Complexity | Reliability | Demo value | Notes                          |
| ------------------------------------ | ----: | ---------: | :---------: | :--------: | ------------------------------ |
| In-memory embeddings + NumPy cosine  |    £0 |        Low |    High     |    High    | ✅ Chosen (V1)                 |
| Postgres + pgvector                  |    £0 |     Medium |    High     |    High    | Good V2 scale path             |
| Hosted vector DB (Pinecone/Weaviate) |    ££ |    Low/Med |    High     |    High    | Adds ongoing cost + CI mocking |
| Add LLM rewriter (local/hosted)      | £0–££ |   Med/High |     Var     |   Medium   | Not needed for 5–10 FAQs       |

---

## 4. Architecture (V1)

```text
Client → FastAPI /faq/ask
│
▼
Retrieval service
(MiniLM embeddings in mem,
NumPy cosine top-1)
│ (score)
┌───────┴────────┐
│ score ≥ thr │ score < thr
▼ ▼
Return FAQ SMTP (MailHog)
answer+source (question + context)
```

---

## 5. Data & Config

-   **FAQ file:** `data/faqs.yaml`
    ```yaml
    - id: faq-001
      question: "How do I book a demo?"
      answer: "Use the /bookings endpoint or email demo@example.local."
      tags: ["booking", "demo"]
    ```
-   **Env (.env/pydantic-settings):**
    -   FAQ_CONFIDENCE_THRESHOLD=0.60
    -   SMTP_HOST=localhost
    -   SMTP_PORT=1025
    -   SMTP_FROM=bot@local.test
    -   HANDOFF_TO=founder@local.test
-   **GDPR/logging:** Truncate or hash questions in logs; so no raw PII

---

## 6. API (V1)

**Endpoint:**

```bash
POST/faq/ask
```

**Request:**

```bash
{ "question": "string (1..500 chars)" }
```

**Response (answer):**

```bash
{ "answer": "string", "score": 0.81, "source_id": "faq-001" }
```

**Response (handoff):**

```bash
{ "handoff": true, "score": 0.42, "question": "..." }
```

---

## 7. Testing strategy

-   **Unit tests:**
    -   Cosine similarity returns correct ordering on a fixed seed set.
    -   Threshold logic branches correctly at boundary conditions.
-   **Integration tests:**
    -   /faq/ask returns correct answers for seed FAQs.
    -   Below-threshold request triggers mocked SMTP.
-   **CI:**
    -   No network calls.
    -   Use MailHog container or mocks.
    -   Pin model version for deterministic embeddings.

---

## 8. Risks & mitigations

-   ARM macOS dependency issues: Pin package versions; maintain requirements.txt.
-   Threshold drift: Start at 0.60; expose env var; test around ±0.05.
-   Scope creep (LLM): Explicitly out of V1; capture in a new ADR if added later.

---

## 9. Upgrade path (V2+)

-   Replace in-memory with pgvector for persistence/scale.
-   Optional LLM rewriter step for improved tone.
-   Swap MailHog with SendGrid/SES and add a simple handoff dashboard.

---

## 10. Consequences

-   Pros: Zero token cost, deterministic behaviour, fast tests, recruiter-friendly demo.
-   Cons: Answers are verbatim, manual curation required.
-   Decision: Proceed with in-memory retrieval + thresholded handoff for Week 4.
