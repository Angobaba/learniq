# Phase 2: Retrieval Tuning - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Improve the RAG retrieval pipeline so it returns complete, relevant textbook passages for both direct questions and multi-turn follow-up queries. Covers chunking, query rewriting, relevance thresholding, TOP_K tuning, and citation display. Does not add new features — improves the existing Q&A experience.

</domain>

<decisions>
## Implementation Decisions

### Chunking Strategy
- Chapter-aware chunking: chunks never cross chapter boundaries, each chunk belongs to exactly one chapter
- Target chunk size ~800 tokens with ~100 token overlap
- Each chunk carries metadata: chapter name and page number (no section title needed)
- Tables and figure captions stay in the same chunk as their surrounding text — don't split them into separate chunks

### Follow-up Behavior
- Use full session history for query rewriting — never lose earlier context
- Auto-detect topic shifts: if student switches from friction to photosynthesis, stop injecting old topic context into the rewrite
- Show the rewritten query to the student: display "I understood your question as: [rewritten query]" so they can see what the system understood
- Graceful partial answers on weak retrieval turns: answer what it can, acknowledge gaps — don't break the chain with a hard fallback

### Citation Display
- Inline references: "(Chapter 12: Friction, p.148)" embedded naturally in the answer text
- Cite only the top 1-2 most relevant source chunks per answer — keep it clean
- Expandable citations: student can click/expand a citation to see the actual retrieved textbook passage in a collapsible section
- For multi-chapter answers, cite only the primary chapter — don't list every chapter referenced

### Fallback Behavior
- Binary confidence: either confident answer with citation, or full fallback — no gray zone partial answers
- Friendly redirect on no results: "I couldn't find this in your textbook. Try asking about [related topic]."
- Different response for off-topic questions: "I'm a science tutor — try asking about [topic suggestions]" vs in-scope "not found in textbook"
- Fallback suggests specific chapters or topics the student could explore

### Claude's Discretion
- Exact relevance score threshold value for chunk filtering
- Query rewriting implementation approach (LangChain history-aware retriever vs custom)
- Topic shift detection method
- Specific Streamlit component for expandable citations

</decisions>

<specifics>
## Specific Ideas

- The 4-turn friction benchmark chain (define → types → examples → which helps walking) should work end-to-end as the gold standard test case
- Citations should show human-readable chapter names like "Chapter 12: Friction, Page 148" — never raw file paths
- The "I understood your question as:" transparency message helps students learn to ask better questions

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-retrieval-tuning*
*Context gathered: 2026-03-14*
