import json
import re
import time

from deepeval.models import DeepEvalBaseLLM
from langchain_groq import ChatGroq

import config


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self, model_name=None, pause=2.0):
        self.model_name = model_name or config.GROQ_MODEL
        self.pause = pause
        self.chat = ChatGroq(model=self.model_name, api_key=config.GROQ_API_KEY, temperature=0)

    def load_model(self):
        return self.chat

    def _call(self, prompt):
        for attempt in range(6):
            try:
                time.sleep(self.pause)
                return self.chat.invoke(prompt).content
            except Exception as e:
                wait = 10 * (attempt + 1)
                print(f"[judge] retry {attempt + 1} after: {str(e)[:90]} (sleep {wait}s)")
                time.sleep(wait)
        raise RuntimeError("judge failed after 6 retries")

    def generate(self, prompt, schema=None):
        if schema is None:
            return self._call(prompt)
        text = self._call(prompt + "\n\nReturn ONLY a valid JSON object. No markdown, no extra text.")
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
        data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        return schema(**data)

    async def a_generate(self, prompt, schema=None):
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model_name