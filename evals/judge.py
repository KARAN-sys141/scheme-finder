import json
import re
import time

from deepeval.models import DeepEvalBaseLLM
from langchain_groq import ChatGroq

import config


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self, model_name=None, pause=2.5):
        self.model_name = model_name or config.JUDGE_MODEL
        self.pause = pause
        self.chat = ChatGroq(
            model=self.model_name,
            api_key=config.GROQ_API_KEY,
            temperature=0,
            max_tokens=3000,
            reasoning_effort="low",
        )

    def load_model(self):
        return self.chat

    def _call(self, prompt):
        for attempt in range(6):
            try:
                time.sleep(self.pause)
                out = self.chat.invoke(prompt).content
                if out and out.strip():
                    return out
                raise ValueError("empty reply")
            except Exception as e:
                wait = 12 * (attempt + 1)
                print(f"[judge] retry {attempt + 1}: {str(e)[:100]} (sleep {wait}s)")
                time.sleep(wait)
        raise RuntimeError("judge failed after 6 retries")

    def generate(self, prompt, schema=None, **kwargs):
        if schema is None:
            return self._call(prompt)
        last = None
        for _ in range(3):
            text = self._call(prompt + "\n\nReturn ONLY a valid JSON object. No markdown, no extra text.")
            try:
                text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
                data = json.loads(text[text.index("{"): text.rindex("}") + 1])
                return schema(**data)
            except Exception as e:
                last = e
        raise RuntimeError(f"judge returned invalid JSON 3 times: {last}")

    async def a_generate(self, prompt, schema=None, **kwargs):
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model_name