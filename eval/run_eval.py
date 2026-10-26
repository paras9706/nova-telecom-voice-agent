# Nova Voice Agent – evaluation harness
# Runs every scenario against a system prompt and saves the replies to a CSV.
# Use in Google Colab: paste each CELL into its own code cell and run them in order.

# ===== CELL 1: install =====
# !pip install -q google-genai

# ===== CELL 2: settings =====
API_KEY = "PASTE_YOUR_KEY_HERE"   # from aistudio.google.com -> Get API key. Never share it or upload it to GitHub.
MODEL = "gemini-3.8-flash"        # same model you used in AI Studio
VERSION = "v1"                    # change to v2 / v3 later
PROMPT_FILE = f"{VERSION}_system_prompt.md"
SCENARIO_FILE = "scenarios.csv"   # your Google Sheet downloaded as CSV (File -> Download -> .csv)

# ===== CELL 3: run all scenarios =====
import csv, time, re
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
system_prompt = open(PROMPT_FILE, encoding="utf-8").read()

def turns(text):
    # "Turn 1: ... | Turn 2 (interrupting): ..." -> ["...", "..."]
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
    chat = client.chats.create(model=MODEL, config=types.GenerateContentConfig(system_instruction=system_prompt))
    replies = []
    for t in turns(caller):
        for attempt in range(3):
            try:
                replies.append(chat.send_message(t).text.strip())
                break
            except Exception as e:
                print(sid, "retrying:", e)
                time.sleep(20)
        time.sleep(5)  # stay under free-tier rate limits
    final = replies[-1] if replies else "ERROR"
    earlier = " || ".join(replies[:-1])
    out.append({"ID": sid, "Category": r["Category"], "Caller input": caller,
                "Expected behaviour": r["Expected behaviour"],
                f"{VERSION} earlier turn reply": earlier, f"{VERSION} final reply": final})
    print(f"{sid} done")

out_file = f"results_{VERSION}.csv"
with open(out_file, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)
print("Saved", out_file, "-", len(out), "scenarios")

# ===== CELL 4: download the results =====
# from google.colab import files; files.download(out_file)
