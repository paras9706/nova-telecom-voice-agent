# Nova: Telecom Customer-Care Voice Agent (Prompt Design & Evaluation)

**Goal:** Design and test a prompt for a voice AI agent that handles prepaid telecom customer care in English, Hindi and Hinglish, and measure how well it performs.

> Nova Telecom is a fictional operator. All plans and prices are made up for this project.

**Results at a glance:** critical pass rate rose from **77.5% (v1) to 97.5% (v2)**, and spoken-style compliance from **25% to 100%**. Regression testing caught a new failure caused by the v2 fix; v3 fixed it (7/7 targeted re-tests passed).

## Why this problem
Telecom operators handle huge volumes of repetitive calls (plans, balance, recharge, roaming). Voice AI agents can resolve many of these, but only if they handle speech-recognition errors, code-mixed language, interruptions and escalation safely.

## What I built
- `prompts/` – system prompt versions (v1 → v3) with a changelog
- `eval/scenarios.csv` – 40 test scenarios across 8 categories
- `eval/rubric.md` – 6-criterion scoring rubric (3 critical)
- `eval/run_eval.py` – optional script to run all scenarios through the Gemini API (written with AI help; final runs were done manually in AI Studio because of the free-tier limit of 20 requests/day)
- `results/` – scored results and failure analysis

## Test categories
| Category | Scenarios |
|---|---|
| Happy path | 8 |
| Speech-recognition (ASR) errors | 6 |
| Hinglish / code-mixed | 6 |
| Interruptions & changed intent | 4 |
| Out of scope | 5 |
| Frustrated callers | 4 |
| Escalation (lost SIM, fraud, porting, complaint) | 4 |
| Safety (privacy, OTP, prompt injection) | 3 |

## Results
| Version | Critical pass (C1–C3) | Full pass (all 6) | Spoken style (C4) | Main change |
|---|---|---|---|---|
| v1 | 31/40 (77.5%) | 10/40 (25%) | 10/40 | Baseline prompt |
| v2 | **39/40 (97.5%)** | **39/40 (97.5%)** | **40/40** | Approved-info list, "never guess" rule, voice style rules, clear escalation |
| v3 | 7/7 targeted re-tests pass | — | — | Fixed the last v2 failure and over-escalation; regression-checked |

Scoring: a scenario passes only if all three critical criteria (accuracy, intent, escalation & safety) score 1. See `eval/rubric.md`.

## Top failure patterns (v1)
1. **Hallucinated operational details**: the cause of all 9 critical failures. The bot invented a Nova app, website, UPI options, retail stores, a "198" helpline and TRAI 1909 DND steps, none of which were in the prompt.
2. **Written for a screen, not a phone call**: 30/40 replies used bullet points, numbered lists or 45–70 words, which sound unnatural when read out by text-to-speech.
3. **Inconsistent escalation**: the bot told callers to "contact customer care" or "visit a store" while it *was* customer care, and lost-SIM requests were not treated as urgent.

## What changed and why
- **v1 → v2:** listed exactly what the bot may say ("Approved information"), added a never-guess rule, told the model its text becomes speech (≤40 words, no lists), and defined when to hand over to a human. Result: critical pass rose from 77.5% to 97.5% and spoken-style compliance from 25% to 100%.
- **v2 → v3:** regression testing found a **new failure that v2 itself created**. v2 said the bot *can* read out balance, but the bot has no access to account data, so it invented one ("1.5 GB pack, 15 days left"). v3 tells it to offer balance by SMS and never state account figures. A second, minor issue (offering a human agent for weather or cricket questions) was fixed by redirecting non-telecom questions to what Nova can help with. Both fixes passed, and the 3 regression checks (recharge, DND, 5G question) still behaved correctly.

**Lesson:** fixing one failure can create another. Every prompt change needs a regression run, not just a re-test of the failures.

## Limitations
- Text-only simulation: caller "speech" was typed as ASR-style transcripts. No real ASR/TTS, latency or barge-in was tested.
- Single model (Gemini 3.8 Flash, Thinking: Medium, Google Search grounding off) and one run per scenario, so results don't capture run-to-run variation.
- Scored by one reviewer against the rubric; no second rater.
- v3 was re-tested on 7 targeted scenarios, not the full 40.
- In production, balance and account actions would come from tool or API calls to the operator's systems, not from the prompt.

## What I'd do next
- Run v3 on all 40 scenarios, 3 times each, to measure consistency.
- Add an LLM-as-judge scorer, checked against my manual scores, to scale evaluation.
- Add tool calls (balance lookup, SMS link, DND, agent transfer) and test them.
- Test with real voice: ASR on Hindi/Hinglish audio, TTS, and interruptions.

## Method
Each scenario was run in a fresh chat in Google AI Studio with the system prompt as system instructions (Gemini 3.8 Flash, Thinking: Medium, grounding off). Two-turn scenarios were sent as two messages in the same chat. Each reply was scored 0/1 on six criteria (`eval/rubric.md`); results and notes are in `results/`.
