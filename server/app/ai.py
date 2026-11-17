"""Provider-independent AI layer. It only writes explanations and summaries: every training decision (what to do today,
how much load, when to back off) comes from the deterministic rules in engine/coach.py and is passed in as facts.

Configure with environment variables (nothing is sent anywhere unless they are set):
  AI_BASE_URL   an OpenAI-compatible chat-completions base URL, e.g. https://api.example.com/v1
  AI_API_KEY    the provider's key
  AI_MODEL      the model name at that provider
Without them the rule-based writer below is used, so the app works the same with no AI at all.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol

SYSTEM = (
    'You are a careful endurance and strength coach. Explain the plan below in plain, encouraging English in under 120 words. '
    'Do not change any numbers, do not add training, do not give medical diagnoses, and never promise hormone or testosterone effects.'
)


class Writer(Protocol):
    name: str

    def write(self, facts: dict) -> str: ...


class RuleWriter:
    name = 'rules'

    def write(self, facts: dict) -> str:
        r = facts.get('readiness', {})
        parts = [r.get('message', '')]
        for slot in ('am', 'pm'):
            s = facts.get(slot)
            if s:
                note = f" {s['note']}" if s.get('note') else ''
                parts.append(f"{'Morning' if slot == 'am' else 'Evening'}: {s['name']} ({s['action']}).{note}")
        n = facts.get('nutrition', {})
        if n:
            parts.append(f"Food: about {n.get('kcal')} kcal and {n.get('protein')} g protein; water {n.get('water_l')} L.")
        if facts.get('pain_advice'):
            parts.append(facts['pain_advice'])
        parts.append(facts.get('sleep', ''))
        return ' '.join(p for p in parts if p)


class OpenAICompatibleWriter:
    name = 'openai-compatible'

    def __init__(self, base_url: str, key: str, model: str, timeout: float = 20):
        self.url = base_url.rstrip('/') + '/chat/completions'
        self.key, self.model, self.timeout = key, model, timeout

    def write(self, facts: dict) -> str:
        body = json.dumps(
            {
                'model': self.model,
                'max_tokens': 300,
                'temperature': 0.3,
                'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(facts, ensure_ascii=False)}],
            }
        ).encode()
        req = urllib.request.Request(self.url, data=body, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.key}'})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.load(r)['choices'][0]['message']['content'].strip()


def writer() -> Writer:
    url, key, model = os.environ.get('AI_BASE_URL'), os.environ.get('AI_API_KEY'), os.environ.get('AI_MODEL')
    if url and key and model:
        return OpenAICompatibleWriter(url, key, model)
    return RuleWriter()


def explain(facts: dict) -> dict:
    w = writer()
    try:
        return {'text': w.write(facts), 'source': w.name}
    except Exception:  # provider down or misconfigured: fall back, never fail the request
        return {'text': RuleWriter().write(facts), 'source': 'rules (AI provider unavailable)'}
