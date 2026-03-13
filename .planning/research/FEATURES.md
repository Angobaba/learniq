# Feature Research

**Domain:** AI-powered textbook-grounded RAG tutor for K-12 (CBSE Grade 8 Science)
**Researched:** 2026-03-14
**Confidence:** MEDIUM — competitor feature sets verified via live product pages (Khanmigo, MATHia, Nolej, Unacademy); Indian ed-tech specifics (Embibe, Toppr) blocked behind JS rendering; RAG quality best practices from LangChain docs and training knowledge (LOW-MEDIUM); bilingual/Hindi specifics from domain knowledge (LOW — verify before building)

---

## Feature Landscape

### Table Stakes (Users Expect These)

These are non-negotiable for a school-demo-ready product. Missing any of these and teachers or students dismiss the product immediately.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Accurate, textbook-grounded Q&A | Core promise: no hallucination. Teachers will test this deliberately. | LOW (exists) | Already built. Citation display already works. |
| Source citations with every answer | Teachers need to verify. Students learn to trust. Industry standard (Khanmigo, Nolej both do this). | LOW (exists) | Already built. Page + source shown. |
| Clear "not found" fallback | If system invents answers to unknowns, trust collapses instantly. | LOW (exists) | Already built. Guardrail in prompts.py. |
| Conversation-aware follow-up handling | Users ask "what about types?" after asking about friction. Current system breaks on this. This is an expectation, not a feature. | MEDIUM | Known gap: each turn is treated independently. Query rewriting needed. |
| Chapter/topic browsing or navigation | Students want to study by chapter, not just ask free-form questions. Demo audiences need to see scope coverage. | MEDIUM | Not built. Could be a sidebar with chapter selector. |
| Confidence / relevance signal | When answer is partial or low-confidence, the system should signal uncertainty rather than present partial answer as complete. | MEDIUM | Not built. Retrieval score thresholding needed. |
| Response appropriate for Grade 8 vocabulary | Answers must be student-accessible, not PhD-level. | LOW | Partially handled in prompt. Needs validation against real Grade 8 phrasing. |
| Session persistence (within session) | Chat history must persist during a session. Reload resets are acceptable but mid-session resets are not. | LOW | Streamlit session state handles this. Verify it works across reruns. |

### Differentiators (Competitive Advantage)

These set LearnIQ apart from generic chatbots, Google search, or textbook PDFs. Prioritize based on demo audience (teachers and school administrators, not just students).

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Adaptive MCQ generation from textbook concepts | Turns passive Q&A into active learning. Khanmigo offers rubric/quiz generation for teachers; LearnIQ can generate student-facing quizzes directly from NCERT content. | HIGH | Requires separate assessment corpus (CBSE question bank, past papers). Not just LLM generation — must be curriculum-aligned. |
| Concept-weakness tagging from quiz performance | Student answers wrong on "types of friction" 3 times → system tags friction as a weak concept. This is the insight teachers cannot get from a textbook. | HIGH | Requires quiz layer to be built first. Data model: student × concept × mastery score. |
| Teacher dashboard: class-level weak-concept heatmap | Shows which concepts the most students are stuck on. Actionable for lesson planning. MATHia's LiveLab is the gold standard. | HIGH | Requires student session data (synthetic initially). Plotly/Streamlit charts sufficient for demo. |
| Chapter mastery summary per student | Visual "how much of Chapter 3 do you know?" progress indicator. Carnegie Learning's Progress Meter is the reference. | MEDIUM | Computed from quiz attempt history. Needs persistent student sessions. |
| Hindi query support (transliterated + native script) | Indian Grade 8 students and parents in Tier 2/3 cities communicate in Hindi. Unique in the RAG-textbook-tutor space. | HIGH | Translation layer: detect language → translate to English → retrieve → answer in Hindi. Bhashini API is the planned approach. Verify Bhashini API stability before building. |
| CBSE-pattern question types (MCQ + short answer + assertion-reason) | CBSE exams use specific question formats. Generic quiz generators do not match these formats. This matters to teachers evaluating the product. | MEDIUM | Assertion-reason format is CBSE-specific and not found in Western ed-tech tools. |
| Benchmark-driven retrieval quality transparency | Show a live eval: "LearnIQ answers X% of benchmark questions correctly." Builds trust with technical buyers. No competitor shows this. | MEDIUM | Benchmark runner already exists in tests/. Needs a UI or report artifact. |
| Socratic guided response mode | Instead of giving direct answers, the system asks guiding questions to help the student arrive at the answer. Khanmigo's core differentiator. | HIGH | Prompt-engineering heavy. Requires a mode toggle. Risk: students find it frustrating for exam prep. |
| Contextual hint system for quiz wrong answers | When a student gets a quiz question wrong, provide a hint pointing to the relevant textbook page — not the answer. | MEDIUM | Links quiz response back to RAG retrieval. Reinforces the textbook-grounding value. |

### Anti-Features (Commonly Requested, Often Problematic)

These will be requested. Document why to not build them so scope creep is pre-empted.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Video content / video explanations | "Kids learn better from video." Teachers will ask for this. | Storage and bandwidth cost. Out of scope per PROJECT.md. Distracts from the RAG differentiation story. | Link to existing NCERT/YouTube videos by chapter. No hosting needed. |
| OAuth / social login (Google, parent accounts) | "We need student accounts for the school." | Engineering cost disproportionate to demo value. Privacy/FERPA/DPDP compliance complexity for school data. | Use class code or teacher-assigned demo sessions. Defer auth to post-PMF. |
| Real-time collaborative features (peer study rooms, live polls) | Ed-tech platforms like ClassIn offer this. | Not a tutoring feature — it is classroom management. Completely different product surface. | If school wants this, point to Teachmint or ClassIn. LearnIQ's value is the grounded RAG, not collaboration. |
| Gamification (badges, leaderboards, XP) | Duolingo-style engagement. Parents and students ask for this. | Adds weeks of UI work with zero retrieval value. Leaderboards can harm low-performing students. | Progress indicators (chapter mastery bars) provide motivation without competition. |
| Page-aware lookup ("What is on page 65?") | Seems natural for a textbook tutor. | LearnIQ uses semantic chunking, not page-indexed retrieval. Page numbers are unreliable after PDF chunking. Out of scope per PROJECT.md. | Cite chapter title + approximate page as metadata already in chunks. |
| Answer generation from non-NCERT sources | "Can you add CBSE sample papers and teacher notes?" | Destroys the zero-hallucination trust model. Multi-corpus retrieval confuses provenance. | Separate assessment corpus for quiz generation only. Never mix with Q&A retrieval. |
| Mobile app (Android/iOS) | India = mobile-first. Teachers and parents will mention this. | Streamlit is not mobile-optimized. React Native / Flutter app is a full separate engineering workstream. | Streamlit works on mobile browsers well enough for demo. Responsive CSS improvements are sufficient pre-PMF. |
| Voice input / text-to-speech output | Accessibility request. Partially valid for Hindi-first users. | Complexity disproportionate to demo value. Voice introduces ASR errors in a multilingual context. | Defer until after Hindi text support is proven. Then evaluate Bhashini's voice capabilities. |

---

## Feature Dependencies

```
[Conversation-aware Q&A]
    └──requires──> [Query rewriting / history injection]
                       └──requires──> [Chat history storage in session]

[Adaptive MCQ quiz]
    └──requires──> [Assessment corpus (CBSE question bank / past papers)]
    └──requires──> [Quiz generation prompt templates]
                       └──enhances──> [Retrieval quality (Phase 2 tuning)]

[Concept-weakness tagging]
    └──requires──> [Adaptive MCQ quiz]
    └──requires──> [Persistent quiz attempt storage]

[Teacher dashboard: weak-concept heatmap]
    └──requires──> [Concept-weakness tagging]
    └──requires──> [Synthetic or real student session data]

[Chapter mastery summary]
    └──requires──> [Concept-weakness tagging]
    └──requires──> [Chapter-to-concept mapping]

[Hindi query support]
    └──requires──> [Language detection layer]
    └──requires──> [Translation service (Bhashini or OpenAI)]
    └──enhances──> [All Q&A features — applies to conversation, quiz, dashboard]

[Contextual hint system]
    └──requires──> [Adaptive MCQ quiz]
    └──requires──> [Retrieval quality (Phase 2 tuning)]

[Benchmark-driven quality transparency]
    └──requires──> [Benchmark dataset (tests/benchmark_runner.py — partial)]
    └──requires──> [Retrieval quality tuning (Phase 2)]

[CBSE-pattern question types]
    └──requires──> [Adaptive MCQ quiz]
    └──requires──> [Assessment corpus with CBSE format examples]

[Socratic guided response mode]
    └──requires──> [Conversation-aware Q&A]  (multi-turn is essential for Socratic dialog)
    └──conflicts──> [Direct answer mode] (requires mode toggle in UI)
```

### Dependency Notes

- **Adaptive quiz requires assessment corpus:** The quiz layer cannot be built with the textbook corpus alone. CBSE question banks and past papers must be sourced before Phase 3 begins. This is explicitly noted as a gap in PROJECT.md.
- **Teacher dashboard requires student data:** The dashboard phase (Phase 4) depends on either synthetic or real session logs. Synthetic data is the right approach for demo; use a data generator before the dashboard sprint.
- **Hindi support is relatively self-contained:** It wraps around the existing Q&A layer via a translation middleware. However, it also applies to quiz responses if built after the quiz layer — plan for bilingual coverage at quiz time, not as an afterthought.
- **Retrieval quality is the foundation:** Phase 2 retrieval improvements (chunk size, TOP_K, query rewriting) unblock both better Q&A (removes false fallbacks) and better quiz generation (better context for concept extraction). It must precede Phase 3 and Phase 4.
- **Socratic mode conflicts with direct-answer mode:** Both cannot be on simultaneously. A UI toggle is required. Socratic mode is a differentiator for demos, but students using it for exam prep revision will want direct answers. Design both modes from Phase 3 onward.

---

## MVP Definition

The app already has a Phase 1 MVP working. This section defines what "school-demo-ready" means — the next milestone MVP.

### Launch With: School-Demo-Ready (v1.1 — Phases 2-3 scope)

Minimum viable product to confidently demo to a teacher or school administrator and have them say "I want this for my class."

- [ ] **Conversation-aware follow-up handling** — Teachers will test this first thing. "What is friction?" → "What are its types?" must work.
- [ ] **Retrieval quality benchmarks passing** — 80%+ accuracy on 15-20 textbook questions. Show the number in the demo.
- [ ] **Chapter/topic selector in UI** — Gives teachers a navigation handle. "Let me show you Chapter 11 — Force and Pressure."
- [ ] **Adaptive MCQ quiz (5-10 questions per chapter)** — The demo moment where it stops being a chatbot and becomes a tutor.
- [ ] **Quiz scoring with correct/incorrect feedback and textbook hint** — Closes the learning loop. Shows grounding.
- [ ] **Weak-concept summary (student-facing, per session)** — "Based on your quiz, review: Types of Friction, Pressure in Fluids." Simple, impactful.

### Add After Validation (v1.2 — Phase 4 scope)

Once a school trial is confirmed or a pilot is running.

- [ ] **Teacher dashboard: class weak-concept heatmap** — Trigger: at least 2 teachers or 1 class using the product.
- [ ] **Chapter mastery progress bar per student** — Trigger: students are taking quizzes regularly.
- [ ] **Session-level analytics export (CSV)** — Trigger: teacher asks for data to share with principal.

### Future Consideration (v2+)

Defer until product-market fit is established.

- [ ] **Hindi/bilingual support** — High value for scale, but Phase 5 is the right time. Risk of under-delivering if rushed.
- [ ] **Socratic guided mode** — Differentiating but complex. Validate demand with teachers first.
- [ ] **CBSE assertion-reason question format** — Nice-to-have after core MCQ is proven.
- [ ] **Benchmark transparency dashboard (public)** — Useful for investor/GTM storytelling, not demo-critical.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Conversation-aware follow-up (query rewriting) | HIGH | MEDIUM | P1 |
| Retrieval quality benchmarks | HIGH | MEDIUM | P1 |
| Chapter/topic selector in UI | HIGH | LOW | P1 |
| Adaptive MCQ quiz generation | HIGH | HIGH | P1 |
| Quiz scoring + textbook hint on wrong answer | HIGH | MEDIUM | P1 |
| Weak-concept summary (student-facing) | HIGH | MEDIUM | P1 |
| Confidence/relevance signal in UI | MEDIUM | MEDIUM | P2 |
| Teacher dashboard: weak-concept heatmap | HIGH | HIGH | P2 |
| Chapter mastery summary per student | MEDIUM | MEDIUM | P2 |
| CBSE-pattern question types (assertion-reason) | MEDIUM | MEDIUM | P2 |
| Contextual hint system for wrong quiz answers | MEDIUM | MEDIUM | P2 |
| Hindi query support | HIGH | HIGH | P2 |
| Benchmark-driven quality transparency (UI) | MEDIUM | LOW | P2 |
| Socratic guided response mode | MEDIUM | HIGH | P3 |
| Session analytics export (CSV) | LOW | LOW | P3 |
| Voice input / TTS | LOW | HIGH | P3 |
| Mobile optimization | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for school-demo-ready milestone
- P2: Should have — add in Phase 4-5 sprint
- P3: Nice to have — future consideration post-PMF

---

## Competitor Feature Analysis

| Feature | Khanmigo | MATHia (Carnegie) | Nolej AI | LearnIQ Approach |
|---------|----------|-------------------|----------|------------------|
| Grounded Q&A with citations | Yes (Khan content) | Partial | Yes (uploaded docs) | Yes — NCERT exclusive |
| Quiz/assessment generation | Yes (teacher-facing) | Yes (adaptive) | Yes (15+ formats) | CBSE-aligned MCQ + short answer |
| Teacher analytics | Yes (on-demand summaries) | Yes (LiveLab, APLSE) | No | Concept heatmap + mastery trend |
| Adaptive difficulty | No (concept-based guidance) | Yes (skill-by-skill) | No | Concept-weakness tagging → harder questions |
| Student-facing weak-concept summary | No | Yes (Progress Meter) | No | Session-level weak-concept list |
| Socratic mode | Yes (core UX) | No | No | Optional mode toggle |
| Bilingual/Hindi support | No | No | No | Planned (Bhashini) — unique differentiator |
| Curriculum alignment (CBSE-specific) | No | No | No | Yes — NCERT + CBSE question patterns |
| RAG over textbook (not general knowledge) | Partial (uses Khan library) | No | Yes (custom knowledge base) | Yes — zero-hallucination, textbook-only |

**Key insight:** No competitor combines all of: RAG-grounded answers from NCERT, CBSE-aligned quiz formats, teacher analytics, and Hindi language support. LearnIQ's moat is this combination, not any single feature.

---

## Retrieval Quality Feature Detail

Retrieval quality is infrastructure, not a user-facing feature. But it is the foundation every other feature depends on. Specific sub-features that are table stakes for a production-quality RAG tutor:

| Sub-Feature | Why Needed | Complexity | Current Status |
|-------------|-----------|------------|----------------|
| Optimal chunk size (800 tokens, 100 overlap) | Current 500-token chunks miss structural questions ("list all types of..."). | LOW | Not yet tuned. Known issue. |
| Conversation-aware query rewriting | Follow-up questions fail without chat history injection. | MEDIUM | Not built. Core gap. |
| TOP_K tuning (target: 6-8) | Too few chunks miss context; too many dilute with noise. | LOW | Not yet tuned. |
| Retrieval score thresholding | Below a score threshold, return "not found" rather than a noisy answer. | MEDIUM | Not built. |
| Benchmark evaluation harness | 15-20 questions + 5 refusal tests. Must pass 80% to claim reliability. | MEDIUM | Benchmark runner exists. Dataset not fully built. |
| Citation validation | Verify cited pages actually contain the answer text. | MEDIUM | Not built. Test stubs exist. |

---

## Sources

- Khanmigo feature set: https://khanmigo.ai/ (live, accessed 2026-03-14) — MEDIUM confidence
- MATHia (Carnegie Learning): https://www.carnegielearning.com/solutions/math/mathia/ (live, accessed 2026-03-14) — MEDIUM confidence
- Nolej AI: https://nolej.io/ (live, accessed 2026-03-14) — MEDIUM confidence
- Unacademy: https://unacademy.com/ (live, accessed 2026-03-14) — MEDIUM confidence
- Microsoft Education AI: https://www.microsoft.com/en-us/education/ai-in-education (live, accessed 2026-03-14) — MEDIUM confidence
- LearnIQ PROJECT.md + README.md: project documentation — HIGH confidence (project source of truth)
- LangChain RAG docs: https://docs.langchain.com (LangChain tutorial content) — MEDIUM confidence
- Embibe, Toppr, Doubtnut: blocked by JS rendering — UNVERIFIED, excluded from analysis
- Indian ed-tech bilingual patterns (Bhashini API): LOW confidence — verify before Phase 5 build

---
*Feature research for: AI-powered CBSE Grade 8 Science RAG tutor (LearnIQ)*
*Researched: 2026-03-14*
