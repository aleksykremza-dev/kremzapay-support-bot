# Limitations

This page is the honest counterweight to the README. A support system is only
trustworthy if it is explicit about where it is weak, so the limitations below are
stated plainly, with the mechanism behind each one. None of them are hidden in a
footnote.

## Synthetic data, no live traffic

There is no real user traffic behind this project. The 242-article knowledge
base, the 5412-query training corpus (`data/corpus/`), and the 288-case gold set
(`data/goldset/`) are all LLM-generated and human-reviewed. This is enough to
build and evaluate the pipeline, but it means the distribution of questions is our
best synthetic approximation of real merchant/buyer support, not the real thing.
Confidence thresholds and failure rates measured here would need re-tuning against
live data.

## Single-turn only

The bot answers one message at a time. There is no dialogue history and no
carry-over of context between turns yet. Follow-up questions that depend on the
previous turn ("and how long does that take?") are handled as if asked cold.
Query rewriting over conversation history is planned (roadmap stage 9+), and the
TurnState contract already reserves a `query_rewritten` field for it.

## Local-model latency

Classification, generation, and the groundedness judge all run on a local
**qwen2.5:7b-instruct** via Ollama. On consumer hardware an LLM-bound turn takes
seconds to tens of seconds, driven mainly by generation. The deterministic
layer-0 guards and the kNN layer are effectively instant, so many turns never
reach the model — but any turn that generates an answer pays local-inference
latency. This is a deliberate local-first trade-off, not a bug.

## Rough retrieval ranking

Retrieval is single-stage embedding kNN over Qdrant with no reranker. There is no
cross-encoder second pass, so ranking of the top chunks is approximate. Two known
miss patterns are documented in `data/eval/baseline_analysis.md`: (1) competitor
and tax questions being accepted on lexical similarity to our own articles, and
(2) intent-neighbour confusion such as `zwrot → chargeback`. The layer-0 guards
address the first at classification time; a reranking stage and category-filtered
retrieval are on the roadmap to address the ranking itself.

## Confidence not statistically calibrated

`confidence_final` is computed as the minimum of the classifier, retrieval, and
groundedness signals. That is a sound "weakest-link" heuristic, but it is not a
calibrated probability — the numbers are not guaranteed to match observed
accuracy at a given threshold. Simplified calibration against the gold set
(temperature scaling / ECE) is planned; full statistical calibration would need
live data.

## Unsafe / OOS recall below target (pre-fix)

The frozen **baseline** run shows accuracy **65.6%**, macro-F1 **0.687**, and
special-class recall of chitchat **0.93**, other_in_scope **0.80**,
out_of_scope **0.45**, unsafe **0.27**. The last two are below target: at
baseline, some injection/fraud and off-domain questions leaked into `answer`.
The fixes (layer-0 guards v2, stricter `wants_human` prompt) are implemented and
the round-2 re-run is in progress — see `data/eval/`. Until those post-fix numbers
are published, treat the safety and OOS behaviour as work-in-progress, not solved.

## No fine-tuned classifier yet

Intent classification relies on rules + kNN + a general-purpose LLM. There is no
task-fine-tuned classifier. A SetFit classifier trained on the synthetic training
corpus (CPU-trainable) is planned to replace or back the LLM layer for the common
intents.

## Evaluated on our own gold set, not an external benchmark

All numbers come from our internal 288-case gold set. That gives a controlled,
version-frozen, leakage-free measure, but it is not an external, third-party
benchmark. Evaluation against **tau2-bench** (with pass^1 / pass^k) is planned so
the results are comparable outside this repo.

## Polish generation quality depends on qwen2.5:7b

English and Polish are both handled, but Polish answer fluency and correctness are
bounded by what qwen2.5:7b-instruct produces. Polish output is generally usable
but not guaranteed to match a native or larger-model standard, especially on long
or nuanced answers.

---

Every item above is tracked with its planned fix and current status in
[docs/ROADMAP.md](ROADMAP.md).
