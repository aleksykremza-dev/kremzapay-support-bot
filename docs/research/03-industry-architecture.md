# How production AI support systems are built

> Design reference compiled 2026-07-21 from 23 public sources (Intercom Fin,
> Sierra, Decagon, NVIDIA NeMo Guardrails, OpenAI Cookbook, Rasa, preprints),
> condensed for this project. Vendor metrics are self-reported.

## Key takeaways

1. A production system is a **pipeline of phases with checks**, not "one smart
   LLM": query refinement and routing -> RAG generation -> answer validation
   (Intercom Fin). At every phase a query can be rejected, redirected, or
   escalated.
2. **Specialized small models beat general LLMs on narrow tasks**: Intercom
   fine-tuned the Snowflake Arctic 2 embedder on ~2M queries (retrieval
   precision 44.79% -> 74.33%, Recall@5 86.15% -> 96.59%); the escalation
   decision is made by a fine-tuned ModernBERT (3 heads: 3-way decision / reason
   out of 8 / triggered guidelines), covering ~90% of cases at >98% accuracy,
   with the LLM handling only the hard tail (triggered by length/complexity,
   not confidence). Sierra orchestrates 15+ models.
3. **Guardrails are a separate layer**, 5 rail types (NeMo): input / dialog /
   retrieval / execution / output; run **asynchronously in parallel** with the
   main call (OpenAI Cookbook, Decagon) to protect latency.
4. **The answer/escalate decision is its own subsystem**: in Fin, uncertainty
   triggers a clarifying question while unsafety triggers automatic escalation
   (two different branches). Escalation itself is 3-way: immediately / offer /
   continue.
5. **Every LLM has its own innate escalation threshold** (HBS/JHU preprint,
   2026: ~56% for one model vs ~91% for another, not predicted by size or
   family), so the escalation behavior of your model must be **measured
   empirically on an eval set before deploy**, not assumed from the prompt.
6. **Prefer silence over confident invention**: every system studied clarifies
   or hands off to a human when uncertain.

## Fin's RAG (3 stages)

Vector search (~40 candidates, for speed) -> reranking with a heavier model
(top 5-10) -> generation from the selected chunks plus user context. Fine-tuning
retrieval on your own data is described as the highest-ROI investment in the
pipeline.

## Classification (complements 02-classifier-spec)

- LLM scenario-selection accuracy degrades as the catalog grows: ~94% @50 ->
  64% @200 -> 13.6% @741. A routing layer is a necessity.
- An LLM classifier with structured output on ~8 classes reaches macro-F1
  ~0.92-0.96 with no training, good enough to start at 5-30 intents.
- Semantic router (embeddings + cosine to route exemplars) is the standard cheap
  layer; SetFit gives an accurate classifier from few examples.
- Routing also decides which mechanism to run: deterministic workflow vs LLM
  answer, so part of the traffic never reaches an LLM at all.

## OOS / fallback (the Rasa reference)

FallbackClassifier: confidence below a threshold (e.g. 0.7) maps to a dedicated
`nlu_fallback` intent, not to the best guess. An explicit out_of_scope intent
trained on real examples; expected-but-unsupported requests get their own
intents with targeted replies. Dialog confidence is separated from NLU
confidence (a second threshold, ~0.4). **Two-Stage Fallback**: re-ask ->
ask to rephrase -> human.
A modern addition: a topical guardrail, a cheap LLM allowed/not_allowed
classifier over a list of permitted topics returning a canned reply (OpenAI
Cookbook). Multi-signal OOS: explicit class + distance threshold + retrieval
signal + topical guardrail; any single signal leaves the main branch.

## Guardrails (NeMo, 5 rails)

| Rail | Stage | What it can do |
|---|---|---|
| Input | before processing | reject/alter input (injections, toxicity, off-topic) |
| Dialog | during the dialog | constrain allowed conversation branches |
| Retrieval | after search | drop KB fragments before they reach the LLM |
| Execution | tool calls | control actions/APIs |
| Output | before sending | hallucinations, fact-checking, policy |

Decagon runs 3 phases: pre-deploy (regression testing), realtime (parallel
fine-tuned models + bad-actor detection), post-dialog (Watchtower reviews
**every** dialog against configurable criteria).

## Vendors

- **Intercom Fin**: 3-phase pipeline, 3-stage RAG, fine-tuned retrieval,
  "encoder for 90%, LLM for 10%" on escalation. The most transparent write-ups.
- **Sierra**: a "constellation" of 15+ models, supervisor models, separated
  components (retrieval / classification / tools / policies / tone), failover
  between providers.
- **Decagon**: Core Agent + Routing Module + Agent Assist (operator copilot) +
  Watchtower; a data flywheel where every dialog improves the system.

## Open-source stack

NeMo Guardrails (all 5 rails) - OpenAI Cookbook / Agents SDK patterns (async
guardrails, topical rail) - Rasa (FallbackClassifier, Two-Stage Fallback; the
newer CALM: LLM command generator + deterministic flows) - LangGraph (CALM vs
LangGraph comparison: 14/14 e2e, ~$0.031 and ~2.6 s per message) - Snowflake
Arctic 2 as a starting embedder with fine-tuning in mind.

## Reference architecture (synthesis)

```
Query -> [Input guardrails: injection/toxicity/PII, async]
      -> [Classification/routing: rules -> embeddings -> LLM cascade;
          deterministic scenarios bypass the LLM]
      -> [OOS/off-topic: explicit class + threshold + topical guardrail]
      -> [RAG: search ~40 -> rerank -> top 5-10 -> LLM with context]
      -> [Output guardrails: groundedness, policy, in parallel]
      -> [Decision: certainty -> answer/clarify; safety or business trigger ->
          escalation with context]
      -> [Post-analysis of every dialog -> improvement loop]
```

Principles: thresholds come from the confusion matrix on an eval set; the
model's escalation behavior is measured empirically; uncertainty leads to
clarification while unsafety leads to escalation; as traffic grows, narrow
tasks move to fine-tuned small models.

## Limitations of this research

Skewed toward Intercom (the only vendor with detailed primary materials);
vendor metrics are self-reported; Rasa covered from legacy docs; the innate
escalation thresholds rest on a single non-peer-reviewed preprint; economics,
latency, multilinguality, and agentic actions are covered thinly.

## Sources

1. https://www.intercom.com/help/en/articles/9929230-the-fin-ai-engine
2. https://fin.ai/research/finetuning-retrieval-for-fin/
3. https://sierra.ai/blog/constellation-of-models
4. https://fin.ai/research/to-escalate-or-not-to-escalate-that-is-the-question/
5. https://decagon.ai/blog/the-ai-agent-engine - https://decagon.ai/resources/designing-layered-guardrails-for-reliable-ai-agents
6. https://github.com/NVIDIA-NeMo/Guardrails - https://docs.nvidia.com/nemo/guardrails/
7. https://developers.openai.com/cookbook/examples/how_to_use_guardrails
8. https://legacy-docs-oss.rasa.com/docs/rasa/fallback-handoff/
9. https://arxiv.org/html/2604.08588v1
10. https://tianpan.co/blog/2026-04-16-intent-classification-agent-routers
11. https://www.respan.ai/articles/intent-classification-with-llms
12. https://www.deepchecks.com/glossary/semantic-router/
13. https://github.com/RasaHQ/calm-langgraph-customer-service-comparison
