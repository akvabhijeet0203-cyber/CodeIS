from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from config import (
    LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_MODEL, OLLAMA_BASE_URL, LLM_MAX_TOKENS, LLM_TEMPERATURE,
)
from utils.logger import get_logger

log = get_logger(__name__)


class LLMClient:
    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider.lower()
        log.info(f"LLM provider: {self.provider}")

        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "groq":
            self._init_groq()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _init_gemini(self):
        if not GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY not set in .env")
        from google import genai
        self._genai_client = genai.Client(api_key=GEMINI_API_KEY)
        log.success(f"Gemini model ready: {GEMINI_MODEL}")

    def _init_groq(self):
        if not GROQ_API_KEY:
            raise EnvironmentError("GROQ_API_KEY not set in .env")
        self._groq_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        log.success(f"Groq model ready: {GROQ_MODEL}")

    def _init_ollama(self):
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            r.raise_for_status()
            log.success(f"Ollama running. Model: {OLLAMA_MODEL}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "gemini":
            return self._gemini_generate(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._groq_generate(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return self._ollama_generate(system_prompt, user_prompt)

    def _gemini_generate(self, system_prompt: str, user_prompt: str) -> str:
        from google import genai
        from google.genai import types
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        try:
            response = self._genai_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=LLM_MAX_TOKENS,
                    temperature=LLM_TEMPERATURE,
                ),
            )
            return response.text.strip()
        except Exception as e:
            log.error(f"Gemini generation error: {e}")
            raise

    def _groq_generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens":  LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
        }
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=self._groq_headers,
                json=payload,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error(f"Groq generation error: {e}")
            raise

    def _ollama_generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": LLM_TEMPERATURE,
                "num_predict": LLM_MAX_TOKENS,
            },
        }
        try:
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["response"].strip()
        except Exception as e:
            log.error(f"Ollama generation error: {e}")
            raise


_client: LLMClient | None = None

def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client