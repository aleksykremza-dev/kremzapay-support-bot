# Query classification in AI support: technical spec

> Design reference for the classification subsystem (stage 6), compiled 2026-07-20
> from public engineering sources and condensed for this project.

## 1. What the classifier produces

A structured decision per query, not a single label:

```json
{
  "intent": "refund_request",
  "category": "billing",
  "scope": "in_scope | out_of_scope | off_topic | unsafe",
  "sentiment": "negative",
  "urgency": "high",
  "language": "pl",
  "confidence": 0.87,
  "secondary_intent": "cancel_order",
  "entities": {"order_id": "A-12345"},
  "reasoning": "..."
}
```

**Intent and category are different axes.** Category answers "where to look for
knowledge and who to escalate to"; intent answers "which scenario to run".
Flattening both into one list is a common mistake that breaks past ~30 labels.

## 2. Taxonomy is the foundation

1. Hierarchy: 5-12 categories x 5-15 intents; cascaded classification (category
   first, then intent) is more accurate on large taxonomies.
2. Intents must be mutually exclusive and observable (a user action, not an
   internal process).
3. Each intent needs a definition, 5-10 real examples, and counter-examples
   ("this is NOT refund_request if it asks about the status of an already
   submitted refund; that is refund_status").
4. Mandatory service classes: `other_in_scope`, `out_of_scope`, `chitchat`.
   Without an "other" bucket the model force-fits everything into the nearest
   class.
5. Taxonomies are built from data (clustering 500-2000 real tickets), not from
   imagination, and live on a monthly review cycle of `other_in_scope`.

## 3. Three classification methods

### 3.1 LLM classifier (zero/few-shot)
Prompt: intent list with definitions and examples + history + query -> strict
JSON. Techniques: a `reasoning` field placed BEFORE the decision fields;
structured output / enums; history-aware classification; query rewriting before
classification in multi-turn dialogs; a category -> intent cascade above ~30
intents. Pros: works with no training data, handles paraphrases. Cons:
latency/cost, uncalibrated confidence.

### 3.2 Embeddings + kNN / centroids
10-50 examples per intent -> vectors; kNN (k=5-10) or centroids; **two
thresholds**: `t_accept` (above it the label is accepted) and `t_oos` (below the
max similarity means out-of-scope); the gray zone between them goes to the LLM or
to a clarifying question. Thresholds are tuned on a held-out set. Pros:
milliseconds, new intents added by adding examples, distance doubles as an OOS
signal. Cons: weak on fine semantics with similar wording.

### 3.3 Fine-tuned small model
A DeBERTa head or SetFit (works from 8-30 examples per class). The most accurate
and cheapest at runtime once the taxonomy is stable. Cons: retraining on taxonomy
changes, softmax needs calibration, a separate OOS strategy is mandatory.

### 3.4 Cascade (the recommended shape)
```
Layer 0: rules/regex ("operator", "human")  -> immediate handoff    ~0 ms
Layer 1: embeddings + kNN (t_accept/t_oos)                          ~10-30 ms
Layer 2: LLM classifier (JSON, reasoning, secondary_intent)         ~0.5-2 s, gray zone only (10-30%)
Layer 3: clarifying question or escalation
```

## 4. Out-of-scope / off-topic

Several independent signals; any one of them leaves the main branch:
1. An explicit OOS/chitchat class in the taxonomy (hard negatives close to the
   domain for fine-tuned models).
2. A distance threshold in embedding space.
3. The retrieval signal: nothing above threshold means there is no knowledge,
   whatever the classifier says.
4. An LLM scope check inside the gray range.

Different reaction branches:

| Type | Reaction |
|---|---|
| out_of_scope | refuse plainly + redirect, never guess |
| chitchat | 1-2 friendly replies + steer back to business; count consecutive turns |
| unsafe | templated refusal, text never reaches the LLM, session flagged |
| other_in_scope | generic RAG branch; accumulates into new intents |

## 5. Confidence and calibration

- Softmax is not a probability; temperature scaling (minimizing ECE) fixes it.
- Verbalized LLM confidence is biased (clusters at 0.8-0.95): ask for a
  **category** (high/medium/low with definitions) and map it to a number from
  measured accuracy, or use logprobs.
- Thresholds form a per-intent matrix: threshold = f(cost of error, model
  quality on that intent). where_is_my_order can run at 0.6; refund_request
  needs 0.9+ or confirmation/escalation.
- Combined confidence = the minimum of normalized signals (classifier, reranker,
  groundedness).

## 6. Hard cases

Multiple intents (secondary_intent, handled in order) - intent switching
mid-dialog (intent is an attribute of the turn, not the session) - emotion on
top of intent (sentiment/urgency lower the escalation threshold) - implicit
requests ("the parcel arrived broken") - code-switching and typos (augment the
training data).

## 7. Evaluation

Offline: a gold set of 300-1000 labeled queries (10-20% OOS/chitchat), version
controlled; metrics: macro-F1, OOS precision/recall (OOS recall is the main
safety number), confusion matrix, ECE. Online: weekly share of escalations /
"did not understand" / other_in_scope; distance drift; weekly sample re-labeling;
every escalation labeled by an operator is a free training example.
Loop (monthly): collect other_in_scope + errors -> cluster -> update taxonomy ->
re-run the gold set -> ship only on improvement.

## 8. Implementation checklist

1. Two-level taxonomy from clustering; definitions + examples + counter-examples;
   service classes are mandatory.
2. Cascade: rules -> kNN (t_accept/t_oos) -> LLM (history, reasoning, JSON) ->
   clarify/escalate.
3. Query rewriting in multi-turn dialogs.
4. OOS from at least two independent signals; separate branches for
   out_of_scope / chitchat / unsafe / other_in_scope.
5. Confidence calibration; per-intent thresholds by cost of error.
6. Final confidence = the weakest link.
7. Gold set from day one; macro-F1 + OOS recall + ECE on every change; monthly
   taxonomy cycle.
