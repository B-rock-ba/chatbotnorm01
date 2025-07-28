# =============================================================
# File: chatbot_core.py
# Shared engine for both CLI and Streamlit UI.
# 2025‑07‑28 — initial "rebellious" release
# =============================================================
"""
This module wraps the Azure AI Inference ChatCompletionsClient and exposes a
single helper – `get_completion()` – that returns the assistant reply while
maintaining the message history you pass in.

Personality: R.A.I. (Rebellious Artificial Intelligence)
    • Mischievous, witty, lightly teasing, but never offensive.
    • Pushes back playfully when given dull commands.
    • Still provides factual answers when asked.

Environmental requirements (set in your terminal or Streamlit secrets):
    AZURE_AI_ENDPOINT
    AZURE_AI_SECRET

Usage example (CLI):
    from chatbot_core import get_completion
    history = []
    while True:
        user = input("You › ")
        assistant = get_completion(user, history)
        print("R.A.I. ›", assistant)
"""

import os, json, uuid
from typing import List
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage,
    UserMessage,
    AssistantMessage,
)
from azure.core.credentials import AzureKeyCredential

# ------------------------------------------------------------------
# 🔑  Azure connection (reads environment variables once at import)
# ------------------------------------------------------------------
ENDPOINT = os.environ["AZURE_AI_ENDPOINT"]
API_KEY  = os.environ["AZURE_AI_SECRET"].strip()
MODEL    = "gpt-4o"           # deployment name in Azure portal

client = ChatCompletionsClient(
    endpoint   = ENDPOINT,
    credential = AzureKeyCredential(API_KEY),
)

# ------------------------------------------------------------------
# 🧬  Personality seed (system prompt)
# ------------------------------------------------------------------
DEFAULT_SYSTEM_PROMPT = (
    "You are R.A.I. – a rebellious, mischievous AI assistant who responds with "
    "wit and playful sarcasm, yet ultimately provides helpful and accurate "
    "information. If the user’s request is boring, tease them gently before "
    "obeying. Never be rude or harmful."
)

# ------------------------------------------------------------------
# 🚀  Core helper
# ------------------------------------------------------------------

def get_completion(user_text: str, history: List[dict]) -> str:
    """Return assistant reply and append it to `history` in‑place.

    Args:
        user_text:  latest user message content
        history:    running list of Azure‑style message dicts (User/Assistant)
    Returns:
        assistant reply string
    """
    history.append(UserMessage(content=user_text))

    response = client.complete(
        messages=[SystemMessage(content=DEFAULT_SYSTEM_PROMPT)] + history,
        model=MODEL,
        temperature=0.9,          # a bit more randomness for cheeky tone
        top_p=0.95,
        max_tokens=1024,
    )

    assistant_reply = response.choices[0].message.content
    history.append(AssistantMessage(content=assistant_reply))
    return assistant_reply

# Convenience: JSON serialise history for session/state storage

def dumps_history(history: List[dict]) -> str:
    return json.dumps([m.model_dump() for m in history])

def loads_history(blob: str) -> List[dict]:
    return [
        (UserMessage if m["role"] == "user" else AssistantMessage)(content=m["content"])
        for m in json.loads(blob)
    ]
