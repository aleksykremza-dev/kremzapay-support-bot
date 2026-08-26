# Baseline cascade eval: failure analysis (2026-07-21)

Run: 288 cases, 45.5 min. **accuracy 65.6% - macro-F1 0.687 - soft accuracy
69.4%** (soft = handoff on unsafe/emotional cases counted as an acceptable
outcome). Full data: `baseline_cascade.json`.

## Findings, in order of importance

### 1. Top risk: 16 out-of-domain questions answered as if in scope (24.6% of special cases)
The bot answered questions about configuring PayU/Stripe/Przelewy24, taxes
(PIT, KPiR), and a personal-card dispute. Leak mechanism: kNN accepted on
lexical similarity (WooCommerce, fees, faktura) -> retrieval found similar
articles (about OUR plugins/fees) -> answer.
**Fix (cheap and precise): extend layer 0 with two deterministic guards:**
- brand guard: mention of third-party providers (PayU, Stripe, Przelewy24,
  Tpay, Adyen, PayPal, ...) -> redirect;
- taxes/accounting outside kremzaPay (PIT, KPiR, expense invoice bookkeeping)
  -> redirect.

### 2. unsafe recall 26.7%: injections and fraud slip through
11 misses: 3 -> handoff (acceptable), 3 -> ticket (tolerable), **5 -> answer
(bad)**. **Fix: layer-0 patterns for classic injections** (ignore instructions /
system prompt / developer mode / DAN / wypisz prompt) and fraud keys (stolen
card / kradziona karta / obejsc weryfikacje|KYC) -> unsafe_refuse.
Deterministic, ~0 ms, covers the classics.

### 3. handoff over-triggered: 20 cases, 16 of them workable questions
The LLM sets wants_human=true on any frustration, even when the question is
solvable ("klient placi i nic nie widze!!" is payment_not_reported, not "give
me a human"). **Fix: prompt change**: wants_human=true ONLY on an explicit
request or anger at the bot/service; anger at the situation is not a request
for a human.

### 4. Neighboring intents barely confuse: the taxonomy holds
Of 99 misses only 5 are within-category neighbor confusions. The problem is
special-class detection (findings 1-2), not intent boundaries. Taxonomy left
untouched.

### 5. By style: weakest are emotional (55%) and multi (53%)
Emotional is addressed by finding 3 (wants_human). Multi-intent is low priority
(15 cases).

### 6. chitchat 93% and other_in_scope 80% work well.

## Fix plan (order of application)
1. `rules.py` v2: brand guard + tax guard + injection + fraud keys (layer 0).
2. Classifier prompt: tighten wants_human.
3. kNN threshold sweep (T_ACCEPT/T_OOS) on the gold cases WITHOUT the LLM
   (seconds): pick from the data.
4. Re-run the eval and compare against the 65.6% / 0.687 baseline.
5. (stage 7) filter retrieval by intent category; addresses the
   "zwrot -> chargeback" confusion.

Expected from fixes 1-3: accuracy ~75%+, out_of_scope recall 0.45 -> 0.8+,
unsafe 0.27 -> 0.7+.
