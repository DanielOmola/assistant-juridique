import openai
from anthropic import Anthropic
from groq import Groq
from typing import Optional, Dict, Any
import json
openai_client = None
anthropic_client = None
groq_client = None

class LLM_Client():

    def __init__(self, 
                 modele_actif:str
                 , API_KEYS:dict
                 , MODELES_DISPONIBLES:dict
                 ):
        self.API_KEYS = API_KEYS
        self.MODELES_DISPONIBLES = MODELES_DISPONIBLES
        self.modele_actif = modele_actif

        self.test_client()

        print("\n" + "="*50)
        print("✅ Configuration multi-modèles prête !")
        print(f"📊 Modèles disponibles : {len(self.MODELES_DISPONIBLES)}")
        print(f"🎯 Modèle par défaut: {self.modele_actif}")
        print("="*50)

    def get_openai_client(self):
        global openai_client
        if openai_client is None and self.API_KEYS["openai"]:
            openai_client = openai.OpenAI(api_key=self.API_KEYS["openai"])
        return openai_client

    def get_anthropic_client(self):
        global anthropic_client
        if anthropic_client is None and self.API_KEYS["anthropic"]:
            try:
                anthropic_client = Anthropic(api_key=self.API_KEYS["anthropic"])
                print("✅ Client Anthropic initialisé")
            except ImportError:
                print("⚠️ Bibliothèque anthropic non installée. Exécute: !pip install anthropic")
                return None
        return anthropic_client

    def get_groq_client(self):
        global groq_client
        if groq_client is None and self.API_KEYS["groq"]:
            try:
                groq_client = Groq(api_key=self.API_KEYS["groq"])
                print("✅ Client Groq initialisé")
            except ImportError:
                print("⚠️ Bibliothèque groq non installée. Exécute: !pip install groq")
                return None
        return groq_client

    # ========== FONCTION D'APPEL UNIFIÉE ==========
    def call_llm(self, prompt: str, system_prompt: str, model_id: str = None, temperature: float = 0.3) -> Dict[str, Any]:
        """Appelle n'importe quel modèle avec une interface unifiée"""

        if model_id is None:
            model_id = self.modele_actif

        model_info = self.MODELES_DISPONIBLES.get(model_id)
        if not model_info:
            return {"error": f"Modèle {model_id} non trouvé", "content": ""}

        provider = model_info["provider"]

        try:
            # ===== OPENAI =====
            if provider == "openai":
                self.client = self.get_openai_client()
                if not self.client:
                    return {"error": "❌ Clé OpenAI manquante. Ajoute OPENAI_API_KEY dans les Secrets (🔑)", "content": ""}

                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return {
                    "content": response.choices[0].message.content,
                    "model": model_id,
                    "tokens": response.usage.total_tokens,
                    "provider": "OpenAI"
                }

            # ===== ANTHROPIC CLAUDE =====
            elif provider == "anthropic":
                self.client = self.get_anthropic_client()
                if not self.client:
                    return {"error": "❌ Clé Anthropic manquante. Ajoute ANTHROPIC_API_KEY dans les Secrets", "content": ""}

                response = self.client.messages.create(
                    model=model_id,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096
                )
                return {
                    "content": response.content[0].text,
                    "model": model_id,
                    "tokens": response.usage.input_tokens + response.usage.output_tokens,
                    "provider": "Anthropic"
                }

            # ===== GROQ (Llama, Mixtral, Gemma) =====
            elif provider == "groq":
                self.client = self.get_groq_client()
                if not self.client:
                    return {"error": "❌ Clé Groq manquante. Ajoute GROQ_API_KEY dans les Secrets", "content": ""}

                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return {
                    "content": response.choices[0].message.content,
                    "model": model_id,
                    "tokens": response.usage.total_tokens,
                    "provider": "Groq"
                }

            else:
                return {"error": f"Provider {provider} non supporté", "content": ""}

        except Exception as e:
            return {"error": str(e), "content": ""}

    def set_modele(self, model_id):
        """Change le modèle actif"""
        global modele_actif
        if model_id in self.MODELES_DISPONIBLES:
            self.modele_actif = model_id
            return True
        return False

    def get_modele_info(self):
        return self.MODELES_DISPONIBLES.get(self.modele_actif, {})

    def test_client(self):
        # Test avec Groq (gratuit) si tu as la clé
        self.test_prompt="Dis 'Bonjour, je suis prêt' en une phrase"
        self.test_system_prompt="Tu es un assistant utile"

        if self.API_KEYS["groq"]:
            test = self.call_llm(
                prompt = self.test_prompt,
                system_prompt = self.test_system_prompt,
                model_id="llama-3.3-70b-versatile"
            )
            print("Test Groq:", test.get("content", "Erreur"))

        elif self.API_KEYS["openai"]:
            test = self.call_llm(
                prompt = self.test_prompt,
                system_prompt = self.test_system_prompt,
                model_id="gpt-3.5-turbo"
            )
            print("Test OpenAI:", test.get("content", "Erreur"))

        else:
            print("⚠️ Aucune clé valide. Ajoute GROQ_API_KEY ou OPENAI_API_KEY dans les Secrets")