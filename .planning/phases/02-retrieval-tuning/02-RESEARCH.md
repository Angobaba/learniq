# Phase 2: Retrieval Tuning - Research

**Researched:** 2026-03-14
**Domain:** LangChain RAG pipeline (chunking, query rewriting, score thresholding, citations, Streamlit UI)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Chunking Strategy
- Chapter-aware chunking: chunks never cross chapter boundaries, each chunk belongs to exactly one chapter
- Target chunk size ~800 tokens with ~100 token overlap
- Each chunk carries metadata: chapter name and page number (no section title needed)
- Tables and figure captions stay in the same chunk as their surrounding text — don't split them into separate chunks

#### Follow-up Behavior
- Use full session history for query rewriting — never lose earlier context
- Auto-detect topic shifts: if student switches from friction to photosynthesis, stop injecting old topic context into the rewrite
- Show the rewritten query to the student: display "I understood your question as: [rewritten query]" so they can see what the system understood
- Graceful partial answers on weak retrieval turns: answer what it can, acknowledge gaps — don't break the chain with a hard fallback

#### Citation Display
- Inline references: "(Chapter 12: Friction, p.148)" embedded naturally in the answer text
- Cite only the top 1-2 most relevant source chunks per answer — keep it clean
- Expandable citations: student can click/expand a citation to see the actual retrieved textbook passage in a collapsible section
- For multi-chapter answers, cite only the primary chapter — don't list every chapter referenced

#### Fallback Behavior
- Binary confidence: either confident answer with citation, or full fallback — no gray zone partial answers
- Friendly redirect on no results: "I couldn't find this in your textbook. Try asking about [related topic]."
- Different response for off-topic questions: "I'm a science tutor — try asking about [topic suggestions]" vs in-scope "not found in textbook"
- Fallback suggests specific chapters or topics the student could explore

### Claude's Discretion
- Exact relevance score threshold value for chunk filtering
- Query rewriting implementation approach (LangChain history-aware retriever vs custom)
- Topic shift detection method
- Specific Streamlit component for expandable citations

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RETR-01 | System uses optimized chunk size (~800 tokens) and overlap (~100 tokens) for textbook prose | `RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name="gpt-4o-mini", chunk_size=800, chunk_overlap=100)` verified working |
| RETR-02 | System rewrites follow-up queries using conversation history before retrieval | `create_history_aware_retriever` from `langchain_classic.chains` confirmed available with `RunnableBranch` that skips rewrite when no history |
| RETR-03 | System applies relevance score thresholding to filter low-quality retrieved chunks | `search_type="similarity_score_threshold"` with `search_kwargs={"k": 6, "score_threshold": 0.35}` in `as_retriever` confirmed in `VectorStoreRetriever` source |
| RETR-04 | System returns top-k results with tuned k value (~6) for better recall | `k=6` in `search_kwargs` — trivial config change in `retriever.py` |
| RETR-05 | Citations display chapter name and page reference alongside answer text | Requires adding `chapter` key to Document metadata at ingest time; display logic in `qa_chain.py` and `streamlit_app.py` |
| RETR-06 | System handles multi-turn question chains (e.g., define -> types -> examples -> application) | `create_history_aware_retriever` + `st.session_state` for `chat_history` list of `HumanMessage`/`AIMessage` objects |
</phase_requirements>

---

## Summary

This phase upgrades every layer of the existing RAG pipeline without introducing new dependencies or frameworks. The codebase already uses LangChain (via `langchain-classic` 1.0.3), LangChain-Chroma 1.1.0, and Streamlit 1.54.0 — all installed and working. The three main work areas are: (1) re-ingest with chapter-aware 800-token chunks, (2) add query rewriting using `create_history_aware_retriever` from `langchain_classic.chains`, and (3) upgrade citations to show chapter names with expandable Streamlit expanders.

The most important architectural finding is that `langchain-classic` (not the new `langchain` 1.x agent package) is where all classic LCEL chain primitives live. The project's `requirements.txt` pins `langchain>=0.2.0` but the environment actually has `langchain-classic 1.0.3` installed — the planner must update `requirements.txt` to pin `langchain-classic` explicitly so the import paths work correctly. A second critical finding: Chroma's `similarity_score_threshold` search type requires the collection to be created with `collection_configuration={"hnsw": {"space": "cosine"}}` — if the existing `chroma_db` was created without this, re-ingestion (which this phase requires anyway) must include the cosine distance setting.

The chapter-aware chunking requires a preprocessing step to detect chapter boundaries in the PDF before splitting. The NCERT Grade 8 Science PDF has clear chapter headings (e.g., "Chapter 1 – Nutrition in Plants"). The recommended approach is to use PyPDFLoader's page metadata, build a page-to-chapter mapping from the PDF's table of contents or by scanning for heading patterns, then attach `chapter` metadata to each Document before chunking so that `RecursiveCharacterTextSplitter` inherits it.

**Primary recommendation:** Use `langchain_classic.chains.create_history_aware_retriever` for query rewriting, `RecursiveCharacterTextSplitter.from_tiktoken_encoder` for 800-token chunking, `search_type="similarity_score_threshold"` with `score_threshold=0.35` for filtering, and `st.expander` for collapsible citation passages.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| langchain-classic | 1.0.3 | LCEL chains: `create_history_aware_retriever`, `create_retrieval_chain`, `create_stuff_documents_chain` | Contains classic chain primitives that were moved out of `langchain` 1.x; already installed |
| langchain-core | 1.2.19 | `VectorStoreRetriever`, `ChatPromptTemplate`, `MessagesPlaceholder`, `HumanMessage`, `AIMessage` | Foundation layer; required by all langchain packages |
| langchain-chroma | 1.1.0 | Chroma vector store with `similarity_score_threshold` support | Already installed; verified score normalization API |
| langchain-text-splitters | 1.1.1 | `RecursiveCharacterTextSplitter.from_tiktoken_encoder` for token-accurate chunking | Already installed; verified `from_tiktoken_encoder` classmethod |
| tiktoken | >=0.7.0 | Token counting for chunk size | Already in requirements.txt |
| streamlit | 1.54.0 | `st.expander` for collapsible citation passages; `st.session_state` for chat history | Already installed |
| numpy | (installed) | Cosine similarity for topic-shift detection | Available in environment; no new install needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| langchain-openai | >=0.1.0 | `ChatOpenAI` for query rewriting LLM | Already used for answer generation; reuse same instance |
| pypdf | >=4.2.0 | PDF loading with page metadata | Already installed; used in `loader.py` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `create_history_aware_retriever` | Custom rewrite loop | Custom gives more control over topic-shift logic but adds ~50 lines of code with no benefit; use the built-in |
| `RecursiveCharacterTextSplitter.from_tiktoken_encoder` | `RecursiveCharacterTextSplitter` with char-based sizes | Token-based is accurate for prompt budget; char-based would require ~3200 chars to approximate 800 tokens (4 chars/token average) — less predictable |
| `similarity_score_threshold` retriever | Post-retrieval filtering | Post-filter is messier; `similarity_score_threshold` is built into the retriever and filters before the LLM sees anything |

**Installation:**
```bash
pip install langchain-classic>=1.0.3
```
(All other packages are already in requirements.txt and installed.)

---

## Architecture Patterns

### Recommended Project Structure
```
rag/
├── chunker.py          # UPDATE: add chapter-aware chunking + from_tiktoken_encoder
├── retriever.py        # UPDATE: add score threshold + k=6 + history-aware retriever builder
├── qa_chain.py         # UPDATE: chapter metadata in citations, top-1-2 citation limit
├── prompts.py          # UPDATE: query rewrite prompt + updated system prompt for inline refs
├── embeddings.py       # no change
├── loader.py           # no change
└── vector_store.py     # UPDATE: add collection_configuration for cosine distance
app/
└── streamlit_app.py    # UPDATE: chat_history session state + rewritten query display + expander citations
scripts/
└── ingest_textbook.py  # no change needed (uses chunker.py which will be updated)
```

### Pattern 1: Token-Based Chapter-Aware Chunking

**What:** Split documents by token count (not character count), tagging each chunk with its chapter name. Chapter boundary detection uses a page-to-chapter mapping built before chunking.

**When to use:** Ingestion time, before any chunks are added to Chroma.

**Example:**
```python
# Source: langchain_text_splitters API (verified via installed package inspection)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

# Build page→chapter map from PDF table of contents or heading scan
# Example chapter map: {1: "Chapter 1: Nutrition in Plants", 12: "Chapter 2: Microorganisms", ...}
PAGE_TO_CHAPTER: dict[int, str] = {}  # populated by scan_chapter_boundaries()

def chunk_documents(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4o-mini",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # Attach chapter metadata — inherit from page number
    for chunk in chunks:
        page = chunk.metadata.get("page", 0)
        chapter = _lookup_chapter(page, PAGE_TO_CHAPTER)
        chunk.metadata["chapter"] = chapter  # e.g. "Chapter 12: Friction"

    return chunks
```

### Pattern 2: History-Aware Retriever

**What:** `create_history_aware_retriever` from `langchain_classic.chains` wraps a base retriever. When `chat_history` is empty, it passes the input query directly. When history exists, it feeds (input + history) to an LLM to produce a rewritten standalone query.

**When to use:** Every query after the first turn in a conversation.

**Example:**
```python
# Source: langchain_classic/chains/history_aware_retriever.py (read from installed package)
from langchain_classic.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

REWRITE_SYSTEM = (
    "Given a chat history and the latest user question, "
    "reformulate a standalone search query that can be understood without the chat history. "
    "If the question introduces a new topic unrelated to the history, return the question as-is. "
    "Do NOT answer the question — just reformulate it if needed."
)

rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", REWRITE_SYSTEM),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

def build_history_aware_retriever(base_retriever, llm: ChatOpenAI):
    return create_history_aware_retriever(llm, base_retriever, rewrite_prompt)
```

### Pattern 3: Score-Threshold Retriever

**What:** `search_type="similarity_score_threshold"` with `score_threshold` in `search_kwargs` causes the retriever to return only chunks with relevance score >= threshold. Scores are in `[0, 1]` where 1 is most similar.

**When to use:** Every retrieval call to filter out noise. Required for RETR-03.

**Critical requirement:** Chroma collection MUST be created with `collection_configuration={"hnsw": {"space": "cosine"}}` for the score normalization function to work. Without this, `Chroma._select_relevance_score_fn()` raises a `ValueError` because it cannot determine the distance metric.

```python
# Source: langchain_core/vectorstores/base.py (verified from installed package)
# and langchain_chroma/vectorstores.py (verified from installed package)

def get_retriever(vector_store, top_k: int = 6, score_threshold: float = 0.35):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": score_threshold,
        },
    )
```

For vector store creation:
```python
# Source: langchain_chroma Chroma.__init__ signature (verified)
from langchain_chroma import Chroma

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=persist_dir,
    collection_configuration={"hnsw": {"space": "cosine"}},
)
```

### Pattern 4: Topic-Shift Detection

**What:** Compare the cosine similarity between the current query's embedding and the previous query's embedding. If similarity < 0.3, treat it as a topic shift and pass an empty `chat_history` to the retriever (bypassing the rewrite).

**When to use:** Before calling `create_history_aware_retriever` on each turn.

**Recommendation for Claude's Discretion area:** Use numpy cosine similarity on OpenAI embeddings, with threshold = 0.3. This avoids any extra API calls because embeddings are already being computed for retrieval.

```python
# Source: numpy standard usage (numpy already in environment)
import numpy as np

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

def is_topic_shift(
    current_query: str,
    previous_query: str,
    embeddings,
    threshold: float = 0.3,
) -> bool:
    """Returns True if the topic has shifted significantly."""
    if not previous_query:
        return False
    vecs = embeddings.embed_documents([current_query, previous_query])
    sim = _cosine_similarity(vecs[0], vecs[1])
    return sim < threshold
```

### Pattern 5: Expandable Citations in Streamlit

**What:** `st.expander` renders a collapsible section. Use it to show the retrieved passage text after the main answer.

**When to use:** After each answer that has citations. Label the expander with the human-readable citation string.

**Recommendation for Claude's Discretion area:** Use `st.expander` with the citation label as the title. Pass `expanded=False` so it is collapsed by default.

```python
# Source: streamlit.elements.layouts (verified from installed Streamlit 1.54.0)
# Pattern: render citation expanders after the answer
for i, citation in enumerate(top_citations[:2]):  # top 1-2 only per decision
    chapter = citation["chapter"]
    page = citation["page"]
    label = f"{chapter}, Page {page}"
    with st.expander(label, expanded=False):
        st.markdown(citation["passage"])  # the raw chunk text
```

### Pattern 6: Storing Chat History in Streamlit Session State

**What:** `st.session_state` persists across reruns within a browser session. Store `chat_history` as a list of `HumanMessage` and `AIMessage` objects — the format `create_history_aware_retriever` expects.

```python
# Source: langchain_core.messages (verified), streamlit session_state (verified)
from langchain_core.messages import HumanMessage, AIMessage

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List[HumanMessage | AIMessage]

# After each Q&A turn:
st.session_state.chat_history.append(HumanMessage(content=question))
st.session_state.chat_history.append(AIMessage(content=answer))
```

### Anti-Patterns to Avoid

- **Passing raw string history to create_history_aware_retriever:** The prompt uses `MessagesPlaceholder("chat_history")` — it must receive a list of `HumanMessage`/`AIMessage` objects, not strings or plain dicts.
- **Using `similarity_score_threshold` without cosine collection config:** Chroma raises `ValueError` at retrieval time if the collection distance metric is undefined. Always create the collection with `{"hnsw": {"space": "cosine"}}`.
- **Re-using the old chroma_db after changing chunk settings:** The existing `chroma_db` directory has 500-char chunks. Any score threshold test on that store is invalid. Re-ingest first.
- **Setting score_threshold too high:** Values above 0.5 will filter out most textbook chunks for textbook content (NCERT prose is dense and specific). Start at 0.35 and only raise if hallucinations appear.
- **Rebuilding the vector store on every app start:** Chroma's `from_documents` overwrites the collection. Use `load_vector_store` (existing) for app startup; only `build_vector_store` in the ingest script.
- **Injecting old topic's rewritten query into a new topic:** The CONTEXT.md requires topic-shift detection. Without it, "What about in animals?" after a friction discussion would retrieve friction chunks (catastrophic). Always check cosine similarity before injecting history.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Query rewriting with chat history | Custom prompt-then-retriever loop | `create_history_aware_retriever` from `langchain_classic.chains` | Built-in `RunnableBranch` handles the "no history → pass through" case correctly; custom loop would need to replicate this edge case |
| Score thresholding | Post-retrieval Python filter on similarity scores | `search_type="similarity_score_threshold"` in `as_retriever` | VectorStoreRetriever handles `k`, `score_threshold`, and empty-result warnings in one place |
| Token counting for chunks | Character count with estimated multiplier | `RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name="gpt-4o-mini")` | tiktoken gives exact token counts for the specific model's tokenizer; character estimates can be off by 30-40% |
| Collapsible citation UI | Custom HTML/CSS in Streamlit | `st.expander` | Native Streamlit component, no unsafe HTML injection, works with Streamlit's rerun model |
| Cosine normalization for Chroma scores | Custom distance-to-similarity formula | `collection_configuration={"hnsw": {"space": "cosine"}}` + built-in normalization | Chroma's `_cosine_relevance_score_fn` applies the correct formula; custom formula would diverge from Chroma's internal distance representation |

**Key insight:** Every problem in this phase has a built-in LangChain or Streamlit solution. The risk is not missing libraries — it is misconfiguring the existing ones (wrong distance metric, wrong import path for classic chains).

---

## Common Pitfalls

### Pitfall 1: Wrong Import Path for Classic Chains

**What goes wrong:** `from langchain.chains import create_history_aware_retriever` raises `ImportError` because LangChain 1.x moved classic chains to `langchain-classic`.

**Why it happens:** `langchain` 1.x is now an agent framework built on LangGraph. Classic LCEL chain functions (`create_history_aware_retriever`, `create_retrieval_chain`, `create_stuff_documents_chain`) live in `langchain-classic`.

**How to avoid:** Always import from `langchain_classic.chains`, never from `langchain.chains`.

**Warning signs:** `ImportError: cannot import name 'create_history_aware_retriever' from 'langchain.chains'`

### Pitfall 2: Chroma Missing Cosine Distance Config

**What goes wrong:** `vector_store.as_retriever(search_type="similarity_score_threshold", ...)` raises `ValueError: No supported normalization function for distance metric of type: None` at query time.

**Why it happens:** By default, Chroma uses L2 (Euclidean) distance for HNSW. The `similarity_score_threshold` search type calls `_select_relevance_score_fn()` which checks the collection's `hnsw.space` config. If it is `None` (default), the function raises.

**How to avoid:** Add `collection_configuration={"hnsw": {"space": "cosine"}}` to both `Chroma.from_documents()` (in `vector_store.py`) and `Chroma()` constructor (in `load_vector_store`). Since this requires changing the collection schema, a full re-ingest is needed.

**Warning signs:** `ValueError: No supported normalization function for distance metric of type: None.`

### Pitfall 3: Stale Vector Store After Re-Chunking

**What goes wrong:** Score thresholds behave erratically because the vector store has mixed chunks from old (500-char) and new (800-token) ingestion.

**Why it happens:** `Chroma.from_documents()` in `build_vector_store` overwrites the collection, but only if the user re-runs the ingest script. If they skip re-ingestion, the old embeddings remain.

**How to avoid:** The ingest script must explicitly delete the existing `chroma_db` directory before re-ingesting. Document this as a required step. Add a warning message to the ingest script output.

**Warning signs:** Answer quality degrades, score distributions look bimodal.

### Pitfall 4: Topic-Shift Detection Adds an Embedding API Call

**What goes wrong:** Calling `embeddings.embed_documents([query, prev_query])` on every turn doubles embedding API calls, doubling latency and cost.

**Why it happens:** Naively computing both embeddings fresh on each turn.

**How to avoid:** Cache the previous query's embedding in `st.session_state`. Only compute the current query's embedding fresh; retrieve the previous embedding from session state.

**Warning signs:** Latency doubles for multi-turn conversations.

### Pitfall 5: requirements.txt Missing langchain-classic

**What goes wrong:** `pip install -r requirements.txt` in a fresh environment does not install `langchain-classic`, causing `ImportError` at runtime.

**Why it happens:** The current `requirements.txt` pins `langchain>=0.2.0` (the new agent package), which does not include `langchain_classic`.

**How to avoid:** Add `langchain-classic>=1.0.3` to `requirements.txt` explicitly.

**Warning signs:** `ModuleNotFoundError: No module named 'langchain_classic'` on a fresh install.

### Pitfall 6: chat_history Format Mismatch

**What goes wrong:** `create_history_aware_retriever` receives `chat_history` as a list of dicts (`{"role": "user", "content": "..."}`) instead of `HumanMessage`/`AIMessage` objects. The `MessagesPlaceholder` template formats them incorrectly, causing the LLM to receive garbled history.

**Why it happens:** The current `streamlit_app.py` stores messages as `{"role": "...", "content": "..."}` dicts for display. If the same list is passed to `create_history_aware_retriever`, it will fail or produce incorrect rewrites.

**How to avoid:** Maintain two separate lists in `st.session_state`: `messages` (dicts, for display) and `chat_history` (LangChain message objects, for the retriever). Keep them in sync after each turn.

**Warning signs:** The rewritten query includes literal strings like `"{'role': 'user', 'content': '...'}"`.

---

## Code Examples

Verified patterns from installed package source code and API inspection:

### Complete Conversational RAG Chain

```python
# Source: langchain_classic/chains/history_aware_retriever.py and retrieval.py
# (read from C:/Users/angoswami/AppData/Roaming/Python/Python314/site-packages/)
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Step 1: Build rewrite prompt
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Given a chat history and the latest user question, "
        "reformulate a standalone search query without the chat history context. "
        "If the question is on a completely new topic, return it unchanged. "
        "Output ONLY the reformulated query — no explanation."
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Step 2: Build the history-aware retriever
history_retriever = create_history_aware_retriever(llm, base_retriever, rewrite_prompt)

# Step 3: Build the answer chain
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT_TEMPLATE),  # existing system prompt with {context}
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
combine_docs_chain = create_stuff_documents_chain(llm, answer_prompt)

# Step 4: Full retrieval chain
rag_chain = create_retrieval_chain(history_retriever, combine_docs_chain)

# Step 5: Invoke
result = rag_chain.invoke({
    "input": question,
    "chat_history": st.session_state.chat_history,  # List[HumanMessage | AIMessage]
})
answer = result["answer"]
context_docs = result["context"]  # List[Document] — for citation display
```

### Chapter-Boundary Detection from PDF

```python
# Source: PyPDFLoader API (verified - returns page metadata with "page" key)
# Pattern: scan page content for chapter headings to build page→chapter map
import re

CHAPTER_HEADING_PATTERN = re.compile(
    r"Chapter\s+\d+[\s\-–:]+(.+)",
    re.IGNORECASE,
)

def build_chapter_map(documents) -> dict[int, str]:
    """Build a mapping of page_number -> chapter_name from loaded PDF pages."""
    chapter_map: dict[int, str] = {}
    current_chapter = "Unknown Chapter"

    for doc in documents:
        page_num = doc.metadata.get("page", 0)
        # Scan first 500 chars of page for a chapter heading
        text_head = doc.page_content[:500]
        match = CHAPTER_HEADING_PATTERN.search(text_head)
        if match:
            current_chapter = f"Chapter {_extract_chapter_num(text_head)}: {match.group(1).strip()}"
        chapter_map[page_num] = current_chapter

    return chapter_map
```

### Retriever with Score Threshold

```python
# Source: langchain_core VectorStoreRetriever source (verified from installed package)
def get_retriever(
    vector_store,
    top_k: int = 6,
    score_threshold: float = 0.35,
):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": score_threshold,
        },
    )
```

### Updated vector_store.py for Cosine Distance

```python
# Source: langchain_chroma Chroma.from_documents signature (verified)
def build_vector_store(chunks, persist_dir=None):
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
        collection_configuration={"hnsw": {"space": "cosine"}},  # REQUIRED for score threshold
    )
    return vector_store
```

### Citation Formatting with Chapter Name

```python
# Pattern: extract top-2 citations using chunk order (first two are highest scored by Chroma)
def _extract_citations(chunks, max_citations: int = 2):
    seen = set()
    citations = []
    for doc in chunks[:max_citations]:
        chapter = doc.metadata.get("chapter", "Unknown Chapter")
        page = doc.metadata.get("page", "?")
        key = (chapter, page)
        if key not in seen:
            seen.add(key)
            citations.append({
                "chapter": chapter,
                "page": page,
                "passage": doc.page_content,  # for expander display
            })
    return citations

# In streamlit_app.py — inline citation in answer prompt:
# The system prompt instructs the LLM to write inline refs like "(Chapter 12: Friction, p.148)"
# based on the [i] source markers already in the context string.
```

### Expandable Citations in Streamlit

```python
# Source: streamlit.elements.layouts expander API (verified from Streamlit 1.54.0)
# Render inline answer first
st.markdown(answer)

# Then render expandable source passages
if citations:
    for citation in citations:
        label = f"{citation['chapter']}, Page {citation['page']}"
        with st.expander(label, expanded=False):
            st.caption("Retrieved passage:")
            st.markdown(f"> {citation['passage']}")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `from langchain.chains import create_history_aware_retriever` | `from langchain_classic.chains import create_history_aware_retriever` | LangChain 1.0 (2025) | Breaking import change — old import raises `ImportError` |
| `RecursiveCharacterTextSplitter(chunk_size=500)` (char-based) | `RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=800)` (token-based) | langchain-text-splitters 0.2+ | Accurate token budgeting for the embedding model |
| `search_type="similarity"` (no filtering) | `search_type="similarity_score_threshold"` | langchain-core 0.1+ | Eliminates low-quality chunks before LLM sees them |
| Default Chroma L2 distance | `collection_configuration={"hnsw": {"space": "cosine"}}` | chromadb 0.5+ / langchain-chroma 0.1+ | Required for `[0,1]` normalized relevance scores |

**Deprecated/outdated in this codebase:**
- `chunk_size=500, chunk_overlap=50` in `chunker.py`: Too small for textbook prose — splits mid-concept. Replace with 800 token / 100 token overlap.
- `TOP_K=4` in `retriever.py`: Too few chunks for multi-part questions. Replace with 6.
- `search_type="similarity"` in `retriever.py`: No quality filtering. Replace with `similarity_score_threshold`.
- `source = os.path.basename(c["source"])` in `streamlit_app.py`: Displays raw filename. Replace with `chapter` metadata field.

---

## Open Questions

1. **Chapter Boundary Detection Accuracy**
   - What we know: NCERT Class 8 Science PDF has clearly headed chapters. PyPDFLoader loads one Document per page with `page` metadata.
   - What's unclear: Whether chapter headings always appear at the top of the first page of each chapter, or sometimes mid-page after other content (e.g., continuation of a previous chapter).
   - Recommendation: Implement the regex scan on the first 500 characters of each page. Add a manual override map as a fallback for chapters that don't match the pattern. Validate by printing the chapter map before ingestion.

2. **Optimal score_threshold Value**
   - What we know: Scores from `similarity_search_with_relevance_scores` are in `[0,1]` with cosine distance. Typical textbook RAG thresholds are 0.3–0.45.
   - What's unclear: The actual score distribution for NCERT Grade 8 Science chunks without seeing real retrieval runs. 0.35 is a reasonable starting point but the planner should include a calibration task.
   - Recommendation: Start at 0.35. Log score distributions for the 4-turn friction benchmark. Raise if answers are hallucinating; lower if fallback triggers too often.

3. **requirements.txt Pin Strategy**
   - What we know: `langchain-classic` must be explicitly added. The current `langchain>=0.2.0` pin refers to the 1.x agent framework, not classic chains.
   - What's unclear: Whether pinning `langchain-classic>=1.0.3` alongside `langchain>=1.0.0` creates any dependency conflicts with `langchain-community` or `langchain-openai`.
   - Recommendation: Pin `langchain-classic>=1.0.3` and update `langchain>=1.2.0` to match the installed version. Test with `pip install -r requirements.txt` in a fresh virtualenv.

---

## Sources

### Primary (HIGH confidence)
- Installed package source — `langchain_classic.chains.history_aware_retriever` (read from `C:/Users/angoswami/AppData/Roaming/Python/Python314/site-packages/langchain_classic/chains/history_aware_retriever.py`)
- Installed package source — `langchain_classic.chains.retrieval.create_retrieval_chain` (read from same location)
- Installed package source — `langchain_core.vectorstores.VectorStoreRetriever` (inspected via `inspect.getsource`)
- Installed package source — `langchain_chroma.Chroma.similarity_search_with_relevance_scores` and `_select_relevance_score_fn` (inspected via `inspect.getsource`)
- Installed package source — `langchain_text_splitters.RecursiveCharacterTextSplitter.from_tiktoken_encoder` (inspected via `inspect.getsource`)
- Installed package source — `streamlit.elements.layouts.expander` (inspected via `inspect.getsource`)
- PyPI — langchain 1.2.12 (https://pypi.org/project/langchain/)
- PyPI — langchain-chroma 1.1.0 (https://pypi.org/project/langchain-chroma/)
- PyPI — chromadb 1.5.5 (https://pypi.org/project/chromadb/)
- PyPI — langchain-text-splitters 1.1.1 (https://pypi.org/project/langchain-text-splitters/)

### Secondary (MEDIUM confidence)
- Codebase reading — existing `rag/` modules (current state confirmed for all gap analysis)
- Codebase reading — existing `tests/` and `scripts/` for test patterns and ingest flow

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified by reading installed package source code directly; all imports confirmed working
- Architecture patterns: HIGH — code examples verified by inspecting actual function signatures; `create_history_aware_retriever` source read verbatim
- Pitfalls: HIGH — Chroma cosine config pitfall verified from `_select_relevance_score_fn` source; langchain-classic import path verified from installed package structure
- Score threshold value (0.35): MEDIUM — informed starting point based on typical RAG calibration; exact value depends on actual score distributions which require a live run

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (stable packages — langchain-classic is a legacy stability package; Chroma 1.5.x API unlikely to change for score threshold)
