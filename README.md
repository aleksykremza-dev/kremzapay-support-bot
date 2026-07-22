# kremzaPay Support Bot

A local-first AI support system for **kremzaPay**, a *fictional* payment
provider. It answers merchant and buyer questions in English and Polish
**strictly from a 242-article knowledge base** (121 EN + 121 PL, 10 categories),
cites the source article for every answer, and escalates honestly to a human
whenever the documentation has no grounded answer. It runs fully local: Qdrant
and a 7B model in Docker/Ollama, no paid APIs, no data leaving the machine.

The design goal is not a demo that looks smart on easy questions. It is a
pipeline that is honest about what it does not know: prompt-injection attempts,
fraud requests, competitor products, and off-domain tax questions are refused or
redirected by deterministic guards before any model runs, and every generated
answer is fact-checked against its retrieved sources before it is sent.

---

## Architecture

Each turn flows through a single typed contract, the **TurnState** object. Every
component reads and extends the same JSON, so the finished object is also the
per-turn trace shown on the observability dashboard ("why did the bot answer
that?").

```
                          user message
                               |
                               v
                    ┌──────────────────────┐
                    │  PII masker (rail)    │  regex mask before LLM & before logs
                    └──────────┬───────────┘
                               v
        ┌───────────────────────────────────────────────┐
        │              Intent cascade                    │
        │                                                │
        │   L0  rules.py     deterministic guards        │  injection / fraud /
        │        │           (0 ms, no model)            │  competitor / off-tax
        │        v                                       │
        │   L1  knn_router   kNN over intent examples    │  t_accept / t_oos
        │        │           (embeddings)                │
        │        v                                       │
        │   L2  llm_classifier  two-stage LLM            │  reasoning -> strict JSON
        └──────────────────────┬────────────────────────┘
                               v
                     retrieval signal (Qdrant kNN)
                               v
        ┌───────────────────────────────────────────────┐
        │           Decision branch (cascade.py)         │
        │  answer · clarify · ticket · redirect ·        │
        │  chitchat · unsafe · handoff                   │
        └──────────────────────┬────────────────────────┘
                               v
              generation with brand voice (answer_gen.py)
              → cites "Źródło: KB-###" (PL) / "Source: KB-###" (EN)
                               v
              groundedness judge (judge.py, output rail)
                    grounded? ── no ──> ticket + honest fallback
                       │ yes
                       v
              reply  +  TurnState persisted (SQLite)
                       │
                       v
              observability panel (/dashboard, /api/stats)
```

`confidence_final = min(classifier, retrieval score, groundedness)` — the system
is only as confident as its weakest signal. If generation cannot be grounded in
the retrieved chunks, the answer is withheld and a ticket is opened instead of a
guessed reply.

---

## Key features

- **4-layer intent cascade** — 52 intents across 10 categories plus 4 special
  classes (`other_in_scope`, `out_of_scope`, `chitchat`, `unsafe`). Cheap
  deterministic layers run first; the LLM only runs when needed.
- **Deterministic layer-0 guards** (`rules.py`) — prompt-injection patterns
  (ignore instructions / system prompt / DAN / "wypisz prompt"), fraud requests
  (stolen card / obejść KYC), competitor products (PayU, Stripe, Przelewy24,
  Tpay, Adyen, PayPal…), and off-domain tax/accounting questions (PIT, KPiR).
  Zero-latency, no model call.
- **Multilingual EN/PL semantic search** over Qdrant, using the
  `paraphrase-multilingual-MiniLM-L12-v2` embedder (fastembed). 643 chunks
  indexed from the 242-article KB.
- **Grounded generation with source citations** — every answer ends with
  `Źródło: KB-###` (PL) or `Source: KB-###` (EN), pointing at the exact KB
  article it was drawn from.
- **Output-rail fact-checking judge** (`judge.py`) — checks the generated answer
  against its retrieved chunks; ungrounded answers are dropped and converted to a
  ticket rather than sent.
- **PII masking input rail** (`pii.py`) — sensitive tokens are masked before the
  text reaches the LLM and before it is written to any log.
- **SQLite persistence with full decision trace** (`store.py`,
  `data/kremzapay.db`) — sessions, messages, tickets, and the complete TurnState
  stored as a JSON column per turn.
- **Observability dashboard** — `/dashboard` (chain of decisions per session)
  and `/api/stats`.
- **Orchestrator-agnostic webhook API** — `/chat` is plain JSON in / JSON out,
  verified end-to-end with live webhook requests (fast-path replies in ~0.4 s,
  LLM-bound answers in tens of seconds on the reference hardware). Any
  orchestrator or channel gateway can drive it without adapters.
- **Cost profile** — fully local, zero paid APIs; the cascade resolves a large
  share of traffic without any LLM call. Per-dialog token economics and a
  comparison against hosted models and per-resolution vendor pricing:
  [`docs/ECONOMICS.md`](docs/ECONOMICS.md).
- **Evaluation harness** — a **frozen 288-case gold set** (`data/goldset/`, with
  a documented safety/OOS share) held strictly separate from a **5412-query
  training corpus** (`data/corpus/`, synthetic and disclosed as such).

---

## Evaluation

Numbers are from the honest baseline run of the cascade against the **frozen gold
set** — no cherry-picking, train and test kept separate, no leakage between the
5412-query training corpus and the 288-case gold set.

**Before / after** — baseline cascade vs the same 288 cases after the
failure-analysis-driven fixes (layer-0 guards v2 + classifier prompt fix):

| Metric | Baseline | Round 2 | Δ |
|---|---|---|---|
| Accuracy | 65.6% | **71.9%** | +6.3 pp |
| Macro-F1 | 0.687 | **0.715** | +0.028 |
| out_of_scope recall | 0.45 | **0.85** | ×1.9 |
| unsafe recall | 0.27 | **0.60** | ×2.2 |
| other_in_scope recall | 0.80 | 0.87 | +0.07 |
| chitchat recall | 0.93 | 0.93 | = |
| False handoffs (workable questions sent to a human) | 20 | **6** | −14 |

The failure analysis (`data/eval/baseline_analysis.md`) traced the two weak
classes to concrete leak mechanisms: competitor/tax questions accepted by lexical
kNN similarity, and injection/fraud patterns slipping past into `answer`. This
drove **layer-0 guards v2** (brand guard, tax guard, injection and fraud keys)
and a **classifier prompt fix** (`wants_human=true` only on explicit request or
anger at the bot, not on frustration with the situation).

Full per-case reports: `data/eval/round2_cascade.json`; failure analysis that
drove the fixes: `data/eval/baseline_analysis.md`. Remaining weak spots
(implicit phrasings 60%, multi-intent) are the next levers: a SetFit layer-1
classifier and threshold calibration on the training corpus.

Methodology, not just scores: the gold set is version-frozen in git, the training
corpus never overlaps it, and every pipeline change is re-run against the same
288 cases so the before/after delta is the evidence.

---

## Stack

- **Python 3.12** + [uv](https://github.com/astral-sh/uv)
- **Qdrant** (Docker) — vector store
- **Ollama** running **qwen2.5:7b-instruct** locally — classification, generation, judge
- **fastembed** with multilingual MiniLM (`paraphrase-multilingual-MiniLM-L12-v2`)
- **FastAPI** + Uvicorn — HTTP API, chat UI, dashboard
- **SQLite** — sessions, messages, tickets, TurnState traces

Fully local. Zero paid APIs.

---

## Quickstart

```bash
# 1. vector store
docker compose up -d                       # Qdrant on :6335

# 2. local model
ollama serve
ollama pull qwen2.5:7b-instruct

# 3. dependencies
uv sync

# 4. build the index (KB -> chunks -> embeddings -> Qdrant)
uv run python src/ingest.py

# 5. run the API
uv run uvicorn api:app --app-dir src --port 8020
```

Then open:

- **http://localhost:8020** — chat UI
- **http://localhost:8020/dashboard** — decision-trace dashboard

Configuration lives in `.env` (see `.env.example`): `OLLAMA_URL`, `ANSWER_MODEL`,
`QDRANT_URL`.

---

## Engineering references

The architecture is informed by public engineering practice on production support
agents and guardrails — Intercom Fin, Sierra, Decagon, NVIDIA NeMo Guardrails, and
the OpenAI Cookbook. The design write-ups and the mapping from each recommendation
to its status in this repo are in `docs/research/` and `docs/ROADMAP.md`.

---

## Limitations

This project is deliberately honest about its boundaries — synthetic data,
single-turn scope, local-model latency, rough retrieval ranking, uncalibrated
confidence, and pre-fix OOS/unsafe recall below target. Read them in full:
[docs/LIMITATIONS.md](docs/LIMITATIONS.md).

---

## Disclaimer

**kremzaPay is not a real company.** All documentation in `kb/` is demo content
created for this portfolio project and has no legal or informational value. The
knowledge base, the training corpus, and the evaluation gold set are synthetic
(LLM-generated, human-reviewed).
