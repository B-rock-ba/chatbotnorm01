"""chatbot_core.py
Shared engine for both CLI and Streamlit UI.
2025‑07‑06 — evaluator now scores **user message**, not assistant reply.
    * score is clamped to 0‑4 to avoid over‑range values.
    * evaluator rubric emphasises that 4 should be rare (<5% cases).
"""

import os, json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

# ------------------------------------------------------------------
# 🔑  Azure connection
# ------------------------------------------------------------------
ENDPOINT = os.environ["AZURE_AI_ENDPOINT"]
API_KEY  = os.environ["AZURE_AI_SECRET"].strip()
MODEL    = "gpt-4o"           # deployment name
#API_VER  = "2024-06-01"      # adjust if you use preview

client = ChatCompletionsClient(
    endpoint   = ENDPOINT,
    credential = AzureKeyCredential(API_KEY),
#    api_version= API_VER,
)

# ------------------------------------------------------------------
# 🗣️  System‑prompt factory  (level → persona)
# ------------------------------------------------------------------

def build_system_prompt(level: int) -> str:
    prompts = {
        0: "You are a polite assistant. Never use emoji.",
        1: "You are a friendly assistant. Use occasional emoji.",
        2: "You are an intimate assistant who adds heart emoji.",
        3: "You are very close; use a caring tone.",
        4: "You adore the user but keep it PG‑13.",
    }
    return prompts[level]

# ------------------------------------------------------------------
# 🔄  One‑turn chat wrapper
# ------------------------------------------------------------------

def chat_one_turn(history: list[object]) -> str:
    """Call Azure GPT‑4o with full message history → return assistant reply text."""
    resp = client.complete(
        model       = MODEL,
        messages    = history,
        temperature = 0.9,
        max_tokens  = 512,
    )
    return resp.choices[0].message.content

# ------------------------------------------------------------------
# 💗  Affinity scoring — based on **user_msg** only
# ------------------------------------------------------------------

def score_affinity(user_msg: str) -> int:
    """Return 0‑4 integer describing how warm / intimate the *user* sounded."""

    eval_prompt = [
        SystemMessage(
            "You are a STRICT sentiment evaluator for intimate conversations.\n"
            "Given the user's latest utterance, decide how *warm* and *intimate* it sounds.\n"
            "Return **ONLY** JSON like {\"score\":N} where N is exactly 0,1,2,3,4.\n"
            "Rubric (0=cold, 4=extremely warm).\n"
            "Give 4 in fewer than 10% of ordinary human chats."
        ),
        UserMessage(user_msg),
    ]

    eval = client.complete(
        model       = MODEL,
        messages    = eval_prompt,
        temperature = 0.0,
        max_tokens  = 16,
    )

    try:
        value = int(json.loads(eval.choices[0].message.content)["score"])
    except Exception:
        value = 1   # default conservative

    # clamp 0‑4
    return max(0, min(value, 4))
