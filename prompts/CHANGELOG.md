# Prompt changelog

## v3 (fixes found by regressing v2 on all 40 scenarios)
| v2 issue | Change in v3 | Re-test |
|---|---|---|
| S10: invented the caller's balance and validity (v2 said the bot *can* read balance, but it has no account data) | Bot cannot see account details; offers balance and validity by SMS; never states account figures | Pass |
| S25, S26, S29: offered a human agent for weather, cricket and loans (wastes agent time) | Non-telecom questions: say it can only help with Nova services and name something it can do; no handover | Pass (3/3) |
| Regression checks | S05 recharge, S06 DND, S27 5G/Netflix (should still hand over) | Pass (3/3) |

## v2 (targets the 3 v1 failure patterns)
| v1 failure pattern | Change in v2 |
|---|---|
| Hallucinated operational details (all 9 critical failures) | Added an "Approved information" section covering recharge, balance and DND; added a "never guess" golden rule listing what not to invent (apps, numbers, stores, timelines, reasons for charges) |
| Formatted for screens, not speech (30/40 C4 failures) | Told the model it is on a live phone call and its text becomes speech; banned lists/markdown; capped replies at ~40 words; one question at a time |
| Inconsistent escalation | Stated that Nova *is* the customer-care line; banned "call another number / visit a store"; listed exactly when to connect to an executive, with lost SIM marked urgent |
| Minor issues | Confirm unclear places/numbers; follow the latest request and offer to return to the earlier one; no competitor comparisons or "cheapest/best" claims; approved OTP safety line |

## v1
Baseline: role, plan and roaming tables, three generic style lines.
