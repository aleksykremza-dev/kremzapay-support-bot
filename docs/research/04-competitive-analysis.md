# Competitive analysis: what a market-level AI support agent must do (2026)

> Design reference compiled 2026-07-21 from 22 public sources, condensed for
> this project. Items marked (unverified) come from a single source without
> cross-checking; the rest were cross-checked against multiple sources. Vendor
> numbers are self-reported unless noted.

## 1. Market table stakes

- **Agentic actions are the norm, not a feature**: all 14 agents listed on
  Artificial Analysis (Fin, Zendesk, Agentforce, Decagon, Sierra, Ada, ...)
  execute operations (refunds, subscriptions, workflows), not just answer
  questions. A pure FAQ bot in 2026 is behind the market.
- **Voice is near-universal** (Tidio being the exception); (unverified) voice
  share of interactions 6% (2024) -> 19% (2026); the area is still immature.
- (unverified) Also expected: multilinguality (Fin claims 95 languages),
  omnichannel, analytics, handover, an audit trail of actions, automatic QA of
  every dialog, simulation testing before release.

**For this project:** the core (RAG + classifier + guardrails + escalation) is
covered by notes 02-03; market level additionally requires 2-3 agentic actions
with confirmation plus a decision audit trail.

## 2. Market metrics

### Resolution rate: the headline metric and the main trick
(unverified) Fin claims 67% (40M+ dialogs); independent breakdowns put
production at 45-53%, industry average ~44.8% (top quartile ~58.7%), typical
start 40-60%. By type: FAQ 60-70%, billing 50-60%, borderline policy 20-30%,
multi-step 15-25%.
(unverified) **Deflection is not resolution**: "assumed resolution" (customer
did not reply = counted and billed as resolved) at 15-35% reopen rates turns a
claimed 65% into roughly 45% real.
**Project benchmarks:** >45% genuine resolution is market level; >60% is mature
leaders. A written definition of "resolution" plus a reopen correction is an
instant marker of a serious product.

### Public benchmarks
- **tau-bench / tau2 / tau3 (Sierra Research)** is the de-facto standard:
  simulated customer + policies + tools; domains airline/retail/telecom/
  banking_knowledge (RAG). (unverified) MIT license, so any system can be run
  against it. Leaderboard at taubench.com.
- **pass^k** (success across k repeats) measures reliability rather than
  one-shot success and remains the main watershed (2024: <50% pass^1 and ~25%
  pass^8 for GPT-4-class agents; 2025: ~80% pass^1 but degradation with k
  remains).
- The telecom domain is saturated (99.1%), so it now differentiates the system
  around the model (retrieval, policies, guardrails, escalation), not the model.

**For this project:** run the pipeline on tau2-bench (retail/banking_knowledge)
and report pass^1 and pass^k.

## 3. Pricing and economics (unverified specifics)

The market is moving to outcome-based pricing. Fin $0.99/resolution - Zendesk
~$1.50-2.00/resolution + $50/agent - Agentforce ~$2.00/dialog - Ada
$0.15-0.45/interaction - HubSpot/Quickchat $0.50-0.60 - Decagon ~$95-150K+/year
(per-conversation and per-resolution) - Sierra ~$150K+/year with 3-7 month
onboarding. Reference point: AI ~$0.62/ticket vs a human at $6-12.
Known weaknesses of these models: assumed-resolution billing; unpredictable
costs (the top complaint about Fin); hidden costs (helpdesk sold separately;
Agentforce services at $50-150K).

## 4. Where the leaders fail: differentiation opportunities (from G2/Reddit reviews, unverified)

1. **Hallucinations even in Fin** (confident wrong answers); without grounding
   15-30% of answers are wrong, with grounding <5%. A groundedness layer
   answers the top market complaint.
2. **Zero observability** ("impossible to understand what the AI is thinking",
   123 reviews for Fin). A decision-chain panel (intent -> sources ->
   confidence -> why it answered or escalated) is the strongest differentiator
   and nearly free to build on top of a per-turn trace.
3. Dependence on KB quality (~25% of enterprise KB articles are outdated).
4. Setup complexity and fragmented pricing; ease of launch is an advantage.
5. **No safe gradual rollout** (Fin has no shadow mode); cheap to implement.
6. Enterprise-only leaders (Sierra has no trial, Decagon is managed); the
   self-serve segment is open.
7. Gartner: 80% autonomous resolutions by 2029, BUT 40% of agentic projects
   cancelled by 2027; 60% of customers fear not reaching a human. Fast, plain
   escalation is a market requirement.

## 5. Checklist for a serious project

Core (designed per notes 02-03): full pipeline + guardrails + calibrated
thresholds; three branches: answer / clarify / escalate (safety is not the same
as uncertainty).
Market level (to add):
1. **2-3 agentic actions** with confirmation (payment status, refund, tariff
   change).
2. **An eval report**: tau2-bench + own gold set; pass^1/pass^k; resolution
   rate with a written definition and reopen correction; breakdown by type.
3. **An observability panel** for every dialog.
4. **Shadow mode** (bot drafts, human approves), then autonomy per category.
5. **Automatic QA of every dialog** (LLM judge with a rubric) + audit trail.
6. Compliance at the conceptual level: SOC 2 Type II, GDPR (DPA, EU residency,
   erasure), multi-model support.
7. **A plain limitations page**; against overclaiming vendors it reads as
   maturity.

Demo scenarios: FAQ with sources -> billing with an agentic action ->
out-of-scope refusal -> injection (guardrail) -> hard case with escalation and
context -> metrics panel.

## 6. Frameworks (unverified)

LangGraph is the default for complex agents with an explicit branch graph -
OpenAI Agents SDK (light, 100+ models) - Claude Agent SDK - Rasa CALM (~$0.031
and ~2.6 s/message; Deutsche Telekom reports 50% autonomous resolutions) - not
AutoGen (maintenance mode). The generic recommendation would be LangGraph +
NeMo Guardrails + tau2-bench + a custom classifier. This project keeps the core
hand-built deliberately (learning value); framework migration stays on the
roadmap.

## Sources

tau2-bench: github.com/sierra-research/tau2-bench - artificialanalysis.ai/evaluations/tau2-bench - sierra.ai/blog/tau-bench-shaping-development-evaluation-agents
Comparisons: artificialanalysis.ai/agents/customer-support - braintrust.dev/articles/best-ai-customer-service-agents-2026 - rasa.com/blog/best-ai-agents-for-enterprise
Metrics/economics: usefini.com/guides/deflection-rate-vs-true-resolution-rate-ai-support - fin.ai/learn/roi-ai-customer-service-agents-benchmarks - fin.ai/learn/ai-customer-service-agent-tco-calculator - a16z outcome-based pricing - metronome.com AI pricing field report - getmacha.com pricing models
Weaknesses: G2 (Fin, Zendesk) - clonedesk.ai/blog/intercom-fin-limitations - matrixflows.com chatbot problems
Frameworks/compliance: langfuse.com AI agent comparison - voiceflow.com security & compliance guide
