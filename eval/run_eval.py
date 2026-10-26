"""
Nova voice agent - evaluation script.

Runs every test scenario against one version of the system prompt and saves
the agent's replies to a CSV file, ready for scoring with eval/rubric.md.

Run from the repository root:  python eval/run_eval.py
Requires:  pip install google-genai  and a Gemini API key.
"""

import csv
import os
import re
import time

from google import genai
from google.genai import types

# ---------- Settings ----------
API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_KEY_HERE")  # never commit a real key
MODEL = "gemini-3.8-flash"
VERSION = "v3"                                   # which prompt to test: v1, v2 or v3
PROMPT_FILE = f"prompts/{VERSION}_system_prompt.md"
SCENARIO_FILE = "eval/scenarios.csv"
OUT_FILE = f"results_{VERSION}.csv"

client = genai.Client(api_key=API_KEY)
system_prompt = open(PROMPT_FILE, encoding="utf-8").read()


def turns(text):
    """Split a multi-turn scenario into separate caller messages.

    "Turn 1: UAE pack please. | Turn 2: Sorry, I meant USA."
    -> ["UAE pack please.", "Sorry, I meant USA."]
    """
    if text.strip().lower().startswith("turn 1"):
        parts = text.split("|")
        return [re.sub(r"^\s*Turn \d+[^:]*:\s*", "", p).strip() for p in parts]
    return [text.strip()]


rows = list(csv.DictReader(open(SCENARIO_FILE, encoding="utf-8")))
out = []

for r in rows:
    sid, caller = r["ID"], r["Caller input (simulated speech transcript)"]
    if not sid or not caller:
        continue

    # A fresh chat for every scenario, so tests don't affect each other.
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )

    replies = []
    for t in turns(caller):
        for attempt in range(3):              # retry up to 3 times on API errors
            try:
                replies.append(chat.send_message(t).text.strip())
                break
            except Exception as e:
                print(sid, "retrying:", e)
                time.sleep(20)
        time.sleep(5)                         # stay under rate limits

    out.append({
        "ID": sid,
        "Category": r["Category"],
        "Caller input": caller,
        "Expected behaviour": r["Expected behaviour"],
        "Earlier turn reply": " || ".join(replies[:-1]),
        "Final reply": replies[-1] if replies else "ERROR",
    })
    print(f"{sid} done")

with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print(f"Saved {OUT_FILE} - {len(out)} scenarios")
