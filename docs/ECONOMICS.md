# Economics: what this system costs to run

This page answers the commercial question: what does a dialog cost on this
self-hosted pipeline, what would the same pipeline cost on hosted frontier
models, and how does that compare to per-resolution vendor pricing.

All token figures are **estimates derived from the real prompt sizes of this
pipeline** (classifier stages, generation context of 3 KB chunks, judge check)
weighted by the **real branch distribution measured on the 288-case gold set**
(round 2: 58% answer, 25% ticket, 17% deterministic branches). API prices
change; verify current vendor pricing before quoting.

## Token profile of one dialog turn

| Branch | LLM calls | ~tokens in | ~tokens out |
|---|---|---|---|
| chitchat / redirect / unsafe / handoff (rules or kNN) | 0 | 0 | 0 |
| answer, fast path (kNN accepted) | generation + judge | ~2,400 | ~260 |
| answer, grey zone (2-stage classifier first) | 4 | ~3,250 | ~440 |
| ticket (classifier only) | 2 | ~850 | ~180 |

**Weighted average per turn** (gold-set branch mix): **~2,000 tokens in,
~250 tokens out.**

Key structural point: the cascade means **a large share of traffic never
touches an LLM at all** — deterministic guards and the kNN layer resolve
greetings, attacks, competitor/off-topic questions and confident intents in
milliseconds at zero token cost. On the gold set, 17% of turns used zero LLM
calls and the classifier stages were skipped for every kNN-accepted intent.

## Cost per 1,000 dialog turns (same pipeline, different brains)

| Deployment | $/1K turns | $/turn | Notes |
|---|---|---|---|
| **This system (local 7B, Ollama)** | **$0 marginal** | $0 | One consumer GPU; electricity ≈ $0.02–0.05/h under load. Latency: seconds–tens of seconds on LLM branches |
| Hosted small model (e.g. Claude Haiku class, ~$1/$5 per MTok) | ~$3.3 | ~$0.003 | Near-realtime latency |
| Hosted mid model (GPT-4o class, ~$2.5/$10) | ~$7.5 | ~$0.008 | |
| Hosted strong model (Claude Sonnet class, ~$3/$15) | ~$9.8 | ~$0.010 | Likely accuracy gain on classification and PL generation |
| Hosted frontier (Opus/GPT-5 class, ~$15/$75) | ~$49 | ~$0.05 | Overkill for most branches; sensible only for the judge or hard tail |

The pipeline is model-agnostic: every LLM call goes through one HTTP interface,
so any row above is a config change, not a rewrite. A rational commercial setup
is **tiered**: small hosted model for classifier stages, stronger model for
generation, local or small model for the yes/no judge.

## Against market per-resolution pricing

Vendor pricing observed in the market research (figures partially unverified, mid-2026):

| Vendor model | Price | Implied $/1K resolved |
|---|---|---|
| Intercom Fin | $0.99 per resolution | ~$990 |
| Zendesk AI | ~$1.50–2.00 per resolution + seats | ~$1,500–2,000 |
| Ada | ~$0.15–0.45 per interaction | ~$150–450 |
| **This pipeline on hosted mid model** | tokens only | **~$8–10** |
| **This pipeline self-hosted** | hardware + power | **~$0 marginal** |

Even accounting generously for engineering and hosting overhead, a self-built
pipeline of this architecture runs **two to three orders of magnitude below
per-resolution vendor pricing** at volume — the trade being that you own the
quality work (taxonomy, evaluation, calibration) that vendors amortize across
customers.

## Why self-hosted matters specifically for payments

- **Data sovereignty**: payment-adjacent support traffic (PII, transaction
  details) never leaves the company's infrastructure; the PII rail masks
  card/IBAN/PESEL data before any model call and any log write.
- **Predictable cost**: token-linear or flat, no per-resolution billing
  ambiguity ("assumed resolutions" are a known industry complaint).
- **No vendor lock-in**: the knowledge base, taxonomy, gold set and evaluation
  harness are portable assets; the model behind the pipeline is swappable.

## What this build cost

Development of this project consumed **zero paid API tokens** — all
classification, generation and judging ran on a local qwen2.5:7b-instruct via
Ollama on consumer hardware (GTX 1050 Ti class). The complete stack (Qdrant,
Ollama, FastAPI, SQLite) is free and open source.
