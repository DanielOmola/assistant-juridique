import openai
from anthropic import Anthropic
from groq import Groq
from typing import Optional, Dict, Any
import json
import logging
import os

logger = logging.getLogger(__name__)


class LLM_Client:
    def __init__(self, provider: str, api_key: str, model: str,
                 temperature: float = 0.3, max_tokens: int = 4096):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = self._init_client()

    def _init_client(self):
        try:
            if self.provider == "openai":
                import openai
                return openai.OpenAI(api_key=self.api_key)

            elif self.provider == "anthropic":
                from anthropic import Anthropic
                return Anthropic(api_key=self.api_key)

            elif self.provider == "groq":
                from groq import Groq
                return Groq(api_key=self.api_key)

            elif self.provider == "google":
                from google import genai
                return genai.Client(api_key=self.api_key)
            
            elif self.provider == "deepseek":
                from openai import OpenAI
                # return genai.Client(api_key=self.api_key)
                return OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                
            else:
                raise ValueError(f"Provider non supporté: {self.provider}")

        except Exception as e:
            raise Exception(f"Erreur init client {self.provider}: {str(e)}")

    def call_llm(self, prompt: str, system_prompt: str):
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return {
                    "content": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens,
                    "provider": "openai"
                }

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return {
                    "content": response.content[0].text,
                    "tokens": response.usage.input_tokens + response.usage.output_tokens,
                    "provider": "anthropic"
                }

            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return {
                    "content": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens,
                    "provider": "groq"
                }

            elif self.provider == "google":
                full_content = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                
                generate_content_config = {
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens
                }
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=full_content,
                    config=generate_content_config,
                )
                
                return {
                    "content": response.text,
                    "tokens": 0,
                    "provider": "google"
                }


            elif self.provider == "deepseek":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=False
                )
                
                return {
                    "content": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens,
                    "provider": "deepseek"
                }

        except Exception as e:
            return {
                "error": str(e),
                "content": ""
            }