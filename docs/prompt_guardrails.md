# LearnIQ – Prompt Guardrails

This document describes the answer-grounding rules enforced by the LearnIQ system prompt.

---

## Goal

Ensure that every answer produced by LearnIQ is:
1. **Grounded** – derived only from the retrieved NCERT textbook context.
2. **Honest** – clearly acknowledges when the answer is not in the textbook.
3. **Cited** – includes the source (chapter/page) whenever available.
4. **Age-appropriate** – clear and concise for a Grade 8 student.

---

## System Prompt

The full prompt template is defined in `rag/prompts.py`. The key rules are:

```
Rules you MUST follow:
1. Answer ONLY using information that appears in the provided context.
2. Do NOT use any outside knowledge, general knowledge, or your own training data.
3. If the answer cannot be found in the provided context, respond with the standard
   fallback message.
4. Always cite the source of your answer (chapter title and page number if available).
5. Keep answers concise, clear, and appropriate for a Grade 8 student.
6. Do not speculate, guess, or extrapolate beyond what the context says.
```

---

## Fallback Behaviour

If no relevant chunks are retrieved **or** the retrieved context does not contain the answer, the system responds with:

> "I could not find the answer to your question in the textbook. Please refer to your NCERT Grade 8 Science textbook or ask your teacher."

This fallback is triggered in two places:
1. **Pre-LLM** – in `qa_chain.answer_question()` when `chunks` is empty.
2. **Post-LLM** – the prompt instructs the LLM to produce this message if it cannot find the answer in the provided context.

---

## Why Strict Grounding?

| Risk | Mitigation |
|---|---|
| LLM hallucination | Prompt forbids use of outside knowledge |
| Incorrect science facts | Only textbook-verified content is presented |
| Out-of-syllabus answers | Retrieval is limited to NCERT Grade 8 Science |
| Overconfident wrong answers | Fallback message used when context is insufficient |

---

## Context Construction

Each retrieved chunk is formatted with its source and page number:

```
[1] (Source: NCERT_Class8_Science.pdf, Page: 42)
<chunk text>

[2] (Source: NCERT_Class8_Science.pdf, Page: 43)
<chunk text>
```

This allows the LLM to reference specific sources in its answer and ensures the response is traceable.

---

## LLM Settings

| Setting | Value | Reason |
|---|---|---|
| `temperature` | `0` | Deterministic, factual – no random creativity |
| `model` | `gpt-4o-mini` | Cost-effective with strong instruction-following |

---

## Extending Guardrails

To strengthen grounding in future versions, consider:
- Adding a **post-processing step** that verifies keywords in the answer appear in the retrieved context.
- Implementing **RAGAS** or similar RAG evaluation framework for automated faithfulness scoring.
- Adding a **topic filter** that rejects questions outside CBSE Grade 8 Science scope before retrieval.
