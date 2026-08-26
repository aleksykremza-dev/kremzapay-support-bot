# AI support system at the implementation level (blueprint)

> Design reference compiled 2026-07-21, condensed for this project. Companion
> notes: docs/research/02 (classifier), 03 (industry architecture),
> 04 (competitive analysis).

## 1. System components

| # | Component | Purpose | Typical choice | Here (kremzaPay) |
|---|---|---|---|---|
| 1 | Channels | receive/deliver messages | web widget (WebSocket), email, Telegram Bot API | web chat (stage 9), webhook API for orchestrators |
| 2 | Dialog gateway | sessions, batching, rate limit | FastAPI + Redis | FastAPI (stage 9), sessions in SQLite |
| 3 | Preprocessing + input guardrails | language, PII masker, injection/toxicity | small models + regex | language heuristic + layer-0 guards + PII masker |
| 4 | Classifier/router | intent/scope/sentiment/urgency | cascade (02-classifier-spec section 3.4) | stages 6.3-6.6 |
| 5 | RAG engine | search -> rerank -> generate | embedder + Qdrant + cross-encoder + LLM | fastembed + Qdrant + qwen-7B (rerank on roadmap) |
| 6 | Scenarios/actions | deterministic flows + tool calling | JSON schemas + confirmations | Phase 3: mock kremzaPay panel |
| 7 | Output guardrails + decider | groundedness, policy, final decision | LLM judge + thresholds | stage 7 (judge after generation) |
| 8 | Handoff | operator queue + context | tickets in PostgreSQL | tickets in SQLite (stage 8) |
| 9 | Storage | see section 3 | PostgreSQL + vector DB + Redis + object store | SQLite + Qdrant + files (a deliberate demo simplification) |
| 10 | Observability + loop | traces, metrics, QA, evals | structured logs + dashboard + eval runner | stage 10 + eval harness 6.7 |

**Key principle:** components 3-7 form a pipeline with contracts: every step
takes and returns typed JSON, so any block can be replaced without touching the
rest (the shape Sierra and Decagon describe).

## 2. TurnState: the single pipeline contract

One JSON object that every component extends; the same object doubles as the
trace for the observability panel ("why did the bot answer that?" in ten
seconds):

```json
{
  "turn_id": "...", "session_id": "...",
  "raw_text": "...", "masked_text": "...", "language": "pl",
  "guardrails_in": {"injection": false, "toxicity": false},
  "classification": {"intent": "...", "scope": "...", "confidence": 0.86, "secondary_intent": null},
  "retrieval": {"query_rewritten": "...", "chunks": [{"id": "KB-001", "score": 0.71}]},
  "generation": {"answer": "...", "tool_calls": [], "tokens": 512},
  "guardrails_out": {"grounded": true, "policy_ok": true},
  "decision": {"action": "answer|clarify|ticket|off_topic|unsafe", "confidence_final": 0.71, "reason": "..."},
  "timings_ms": {"classify": 580, "retrieve": 130, "generate": 1850}
}
```

`confidence_final = min(classifier, retrieval score, groundedness)`: the system
is only as confident as its weakest signal. Any action touching a customer
account always requires explicit user confirmation.

## 3. Data and storage (adapted to the SQLite demo)

- `sessions` / `messages` (role, raw/masked text, **turn_state as a JSON
  column**: observability without a separate system);
- `tickets` for escalations: session_id, reason, category, priority, operator
  resolution (future training data);
- a taxonomy registry (`data/taxonomy.json` here): name, definition, examples,
  counter-examples, threshold, version;
- `feedback`: thumbs up/down, reopen flags;
- Qdrant: `kb_chunks` (metadata: article, category, language, version) and
  `intent_examples` (vectors backing the kNN layer);
- `actions_log`: an audit trail of every action (who, what, when, parameters,
  API response).
Rules: PII is masked BEFORE writing to any log and before any LLM call;
retention period + deletion on request (GDPR).

## 4. Knowledge base indexing (offline)

Sources with an owner and a date -> semantic chunking at ~200-500 words
preserving headers/tables -> embed + write (BM25 in parallel for hybrid search
is on the roadmap) -> **a smoke test after every reindex**: a fixed set of ~50
questions must retrieve the same reference articles (protection against
"reindexed and everything silently broke").

## 5. Action layer (agentic)

- Every action is a tool with a JSON schema: `get_payment_status(session_id)`,
  `create_refund(session_id, amount)`, `resend_webhook(session_id)`. The LLM
  never calls an API directly; it requests a tool, and system code executes it
  with validation.
- **Risk classes:** read-only runs immediately; mutating runs after explicit
  confirmation; critical runs only by a human.
- Everything lands in `actions_log`; a tool error must not crash the dialog
  (plain error message + escalation).

## 6. Observability and the loop

Per-dialog panel (the chain of TurnStates) - metrics (resolution rate with a
written definition and a reopen window, escalations by reason, other_in_scope
share, latency, tokens) - automatic QA of every dialog by an LLM judge with a
rubric - an eval runner on every change (release only when macro-F1 / OOS
recall / pass^k do not regress) - the loop: operator replies feed the KB,
errors feed intent examples.

## 7. Build order (blueprint phases mapped to project stages)

1. **MVP pipeline**: gateway + LLM classifier (no cascade) + RAG without
   reranker + thresholds + TurnState log. (~ stages 5-9)
2. **Reliability**: input/output guardrails, groundedness judge,
   OOS/chitchat/unsafe branches, escalation with context, shadow mode.
   (~ 6.6 + 7 + Phase 3)
3. **Quality**: reranker, kNN layer, threshold calibration on the gold set,
   query rewriting. (~ 6.4, 6.7 + roadmap)
4. **Market level**: agentic actions, observability panel, auto-QA, tau2-bench,
   eval report. (= Phase 3 of the plan)

Every stage ends with a gold-set run; the before/after numbers are the
evidence base.
