# Roadmap: research recommendations traced to project status

> Every substantial recommendation from `docs/research/02-05` and where it
> stands in this repo. Statuses: **Done** (with the file or artifact),
> **Planned** (with the reason it is not built yet), **Out of scope** (with the
> blocker). Out of scope here means a real precondition is missing, mainly live
> traffic; synthetic data substitutes for it where it can: the ~5400-query
> training corpus (100 per intent) is kept strictly separate from the frozen
> gold set.

## Classifier (research/02)

| Recommendation | Status |
|---|---|
| Two-level taxonomy, definitions + examples + counter-examples | Done: 52 intents, 10 categories (`data/taxonomy/`) |
| Service classes other_in_scope / out_of_scope / chitchat / unsafe | Done: in the taxonomy |
| Taxonomy built from data (clustering real tickets) | Done via substitute: synthetic corpus ~100/intent (`data/corpus/`) |
| Gold set 300+ with 10-20% OOS, version controlled | Done: 288 cases (`data/goldset/`), 22.6% safety share |
| Cascade: rules -> kNN (t_accept/t_oos) -> LLM -> clarify | Done: `rules.py`, `knn_router.py`, `llm_classifier.py`, `cascade.py` |
| LLM classifier: strict JSON, reasoning before the decision, secondary_intent | Done: `llm_classifier.py` (two-stage) |
| Query rewriting in multi-turn dialogs | Planned: needs dialog history first (single-turn today) |
| OOS from at least 2 independent signals (class + distance + retrieval) | Done: kNN distance + retrieval threshold in `cascade.py` |
| Confidence as categories (high/medium/low), not a number | Done: `llm_classifier.py` |
| Per-intent threshold matrix by cost of error | Planned: thresholds are global today, tuned on the gold set |
| confidence_final = minimum of signals | Done: decision logic in `cascade.py` |
| Temperature scaling / ECE | Planned: simplified calibration against the gold set |
| Fine-tuned classifier (SetFit/DeBERTa) | Planned: SetFit on the training corpus (CPU) |
| macro-F1, OOS recall, confusion matrix on every change | Done: `eval_cascade.py`, results in `data/eval/` |

## Industry architecture (research/03)

| Recommendation | Status |
|---|---|
| Phase pipeline: routing -> RAG -> answer validation | Done: cascade -> retrieval -> generation -> judge |
| Uncertainty -> clarify; unsafety -> escalate (separate branches) | Done: clarify vs unsafe_refuse in `cascade.py` |
| Reranking stage (search ~40 -> rerank -> top 5) | Planned: retrieval is single-stage kNN today |
| Fine-tuning the embedder on own queries | Out of scope: needs millions of real query pairs |
| Guardrails as a separate layer (5 NeMo rails) | Done hand-built: input (rules + PII), output (judge); NeMo itself Planned |
| Async/parallel guardrails | Planned: rails run inline today |
| Empirical measurement of the model's escalation threshold | Done: qwen-7B measured on the gold set (`data/eval/`) |
| Two-Stage Fallback (re-ask -> rephrase -> human) | Partially done: clarify branch exists; a loop counter is Planned |
| Post-analysis of every dialog (Watchtower-style) | Planned: LLM judge with a rubric over stored TurnStates |

## Market level (research/04)

| Recommendation | Status |
|---|---|
| 2-3 agentic actions with confirmation | Planned: get_payment_status / create_refund / resend_webhook against a mock panel |
| Action risk classes + actions_log | Planned: table exists in `store.py`, actions do not yet |
| Observability panel (decision chain) | Done: `/dashboard` over per-turn TurnState traces |
| Shadow mode (drafts for operator approval) | Planned: on top of the ticket queue |
| tau2-bench + pass^1/pass^k | Planned: eval report |
| Resolution rate: written definition + reopen correction | Planned: dashboard metric |
| Automatic QA of every dialog | Planned |
| Limitations page | Done: `docs/LIMITATIONS.md` |
| Voice, omnichannel, 95 languages | Planned late (local whisper + TTS); languages: EN+PL |
| SOC 2 / GDPR compliance | Out of scope: an organizational procedure, not code; demo holds no real PII |
| Frameworks (LangGraph/CALM) | Deliberately hand-built core (learning value); migration path documented |

## Blueprint (research/05)

| Recommendation | Status |
|---|---|
| TurnState as the single pipeline contract + trace | Done: end to end, persisted per turn |
| PostgreSQL + Redis + object storage | Planned: SQLite is a deliberate demo simplification |
| PII masker before LLM and before logs | Done: `pii.py` |
| Smoke test after reindexing (~50 questions) | Planned: to be added to `ingest.py` |
| Versioned taxonomy registry | Done: files in git are the versions |
| 4-phase roadmap (MVP -> reliability -> quality -> market level) | Done: matches the stage map above |
