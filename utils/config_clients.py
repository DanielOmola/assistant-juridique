import openai
from anthropic import Anthropic
from groq import Groq
from typing import Optional, Dict, Any
import json
import logging
import os

# Configuration des logs pour ce module
logger = logging.getLogger(__name__)

openai_client = None
anthropic_client = None
groq_client = None


class LLM_Client():

    def __init__(self, 
                 modele_actif: str,
                 API_KEYS: dict,
                 MODELES_DISPONIBLES: dict
                 ):
        """
        Initialise le client LLM multi-providers
        
        Args:
            modele_actif: Identifiant du modèle par défaut
            API_KEYS: Dictionnaire des clés API
            MODELES_DISPONIBLES: Dictionnaire des modèles disponibles
        """
        logger.info("🚀 Initialisation du LLM_Client")
        
        self.API_KEYS = API_KEYS
        self.MODELES_DISPONIBLES = MODELES_DISPONIBLES
        self.modele_actif = modele_actif
        
        # Vérifier les clés disponibles
        cles_disponibles = [k for k, v in API_KEYS.items() if v]
        logger.debug(f"Clés API disponibles: {cles_disponibles}")
        
        # Tester le client
        self.test_client()
        
        print("\n" + "="*50)
        print("✅ Configuration multi-modèles prête !")
        print(f"📊 Modèles disponibles : {len(self.MODELES_DISPONIBLES)}")
        print(f"🎯 Modèle par défaut: {self.modele_actif}")
        print("="*50)
        logger.info(f"Client initialisé avec modèle: {self.modele_actif}")

    def get_openai_client(self):
        """Retourne le client OpenAI initialisé"""
        global openai_client
        if openai_client is None and self.API_KEYS.get("openai"):
            try:
                openai_client = openai.OpenAI(api_key=self.API_KEYS["openai"])
                logger.debug("✅ Client OpenAI initialisé")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation OpenAI: {str(e)}")
                return None
        return openai_client

    def get_anthropic_client(self):
        """Retourne le client Anthropic initialisé"""
        global anthropic_client
        if anthropic_client is None and self.API_KEYS.get("anthropic"):
            try:
                anthropic_client = Anthropic(api_key=self.API_KEYS["anthropic"])
                logger.debug("✅ Client Anthropic initialisé")
                print("✅ Client Anthropic initialisé")
            except ImportError:
                logger.error("❌ Bibliothèque anthropic non installée")
                print("⚠️ Bibliothèque anthropic non installée. Exécute: !pip install anthropic")
                return None
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Anthropic: {str(e)}")
                return None
        return anthropic_client

    def get_groq_client(self):
        """Retourne le client Groq initialisé"""
        global groq_client
        if groq_client is None and self.API_KEYS.get("groq"):
            try:
                groq_client = Groq(api_key=self.API_KEYS["groq"])
                logger.debug("✅ Client Groq initialisé")
                print("✅ Client Groq initialisé")
            except ImportError:
                logger.error("❌ Bibliothèque groq non installée")
                print("⚠️ Bibliothèque groq non installée. Exécute: !pip install groq")
                return None
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Groq: {str(e)}")
                return None
        return groq_client

    # ========== FONCTION D'APPEL UNIFIÉE ==========
    def call_llm(self, prompt: str, system_prompt: str, model_id: str = None, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Appelle n'importe quel modèle avec une interface unifiée
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Le prompt système
            model_id: Identifiant du modèle (optionnel)
            temperature: Température pour la génération (0.0-1.0)
        
        Returns:
            Dictionnaire avec 'content', 'model', 'tokens', 'provider'
        """
        if model_id is None:
            model_id = self.modele_actif

        model_info = self.MODELES_DISPONIBLES.get(model_id)
        if not model_info:
            logger.error(f"❌ Modèle non trouvé: {model_id}")
            return {"error": f"Modèle {model_id} non trouvé", "content": ""}

        provider = model_info["provider"]
        logger.debug(f"Appel LLM - Modèle: {model_id} (provider: {provider}), température: {temperature}")
        logger.debug(f"Prompt: {prompt[:200]}...")
        logger.debug(f"System prompt: {system_prompt[:100]}...")

        try:
            # ===== OPENAI =====
            if provider == "openai":
                client = self.get_openai_client()
                if not client:
                    logger.error("❌ Clé OpenAI manquante")
                    return {"error": "❌ Clé OpenAI manquante. Ajoute OPENAI_API_KEY dans les Secrets (🔑)", "content": ""}

                logger.debug("📡 Envoi requête OpenAI...")
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                
                logger.info(f"✅ Réponse OpenAI - Tokens: {response.usage.total_tokens}")
                return {
                    "content": response.choices[0].message.content,
                    "model": model_id,
                    "tokens": response.usage.total_tokens,
                    "provider": "OpenAI"
                }

            # ===== ANTHROPIC CLAUDE =====
            elif provider == "anthropic":
                client = self.get_anthropic_client()
                if not client:
                    logger.error("❌ Clé Anthropic manquante")
                    return {"error": "❌ Clé Anthropic manquante. Ajoute ANTHROPIC_API_KEY dans les Secrets", "content": ""}

                logger.debug("📡 Envoi requête Anthropic...")
                response = client.messages.create(
                    model=model_id,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096
                )
                
                total_tokens = response.usage.input_tokens + response.usage.output_tokens
                logger.info(f"✅ Réponse Anthropic - Tokens: {total_tokens}")
                return {
                    "content": response.content[0].text,
                    "model": model_id,
                    "tokens": total_tokens,
                    "provider": "Anthropic"
                }

            # ===== GROQ (Llama, Mixtral, Gemma) =====
            elif provider == "groq":
                client = self.get_groq_client()
                if not client:
                    logger.error("❌ Clé Groq manquante")
                    return {"error": "❌ Clé Groq manquante. Ajoute GROQ_API_KEY dans les Secrets", "content": ""}

                logger.debug("📡 Envoi requête Groq...")
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                
                logger.info(f"✅ Réponse Groq - Tokens: {response.usage.total_tokens}")
                return {
                    "content": response.choices[0].message.content,
                    "model": model_id,
                    "tokens": response.usage.total_tokens,
                    "provider": "Groq"
                }

            else:
                logger.error(f"❌ Provider non supporté: {provider}")
                return {"error": f"Provider {provider} non supporté", "content": ""}

        except TimeoutError as e:
            logger.error(f"❌ Timeout lors de l'appel {provider}: {str(e)}")
            return {"error": f"Timeout: {str(e)}", "content": ""}
            
        except ConnectionError as e:
            logger.error(f"❌ Erreur connexion {provider}: {str(e)}")
            return {"error": f"Erreur connexion: {str(e)}", "content": ""}
            
        except Exception as e:
            logger.error(f"❌ Exception lors de l'appel {provider}: {str(e)}")
            logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
            return {"error": str(e), "content": ""}

    def set_modele(self, model_id: str) -> bool:
        """Change le modèle actif"""
        if model_id in self.MODELES_DISPONIBLES:
            ancien_modele = self.modele_actif
            self.modele_actif = model_id
            logger.info(f"🔄 Changement de modèle: {ancien_modele} → {model_id}")
            return True
        
        logger.warning(f"⚠️ Tentative de changement vers modèle inexistant: {model_id}")
        return False

    def get_modele_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle actif"""
        info = self.MODELES_DISPONIBLES.get(self.modele_actif, {})
        logger.debug(f"Info modèle actif ({self.modele_actif}): {info}")
        return info

    def test_client(self):
        """Test le client avec le modèle par défaut"""
        logger.info("🧪 Test du client LLM")
        
        test_prompt = "Dis 'Bonjour, je suis prêt' en une phrase"
        test_system_prompt = "Tu es un assistant utile"

        if self.API_KEYS.get("groq"):
            logger.debug("Test avec Groq...")
            test = self.call_llm(
                prompt=test_prompt,
                system_prompt=test_system_prompt,
                model_id="llama-3.3-70b-versatile"
            )
            resultat = test.get("content", "Erreur")
            print("Test Groq:", resultat)
            if "erreur" not in resultat.lower():
                logger.info("✅ Test Groq réussi")
            else:
                logger.warning(f"⚠️ Test Groq a retourné: {resultat}")

        elif self.API_KEYS.get("openai"):
            logger.debug("Test avec OpenAI...")
            test = self.call_llm(
                prompt=test_prompt,
                system_prompt=test_system_prompt,
                model_id="gpt-3.5-turbo"
            )
            resultat = test.get("content", "Erreur")
            print("Test OpenAI:", resultat)
            if "erreur" not in resultat.lower():
                logger.info("✅ Test OpenAI réussi")
            else:
                logger.warning(f"⚠️ Test OpenAI a retourné: {resultat}")

        else:
            logger.error("❌ Aucune clé API valide trouvée")
            print("⚠️ Aucune clé valide. Ajoute GROQ_API_KEY ou OPENAI_API_KEY dans les Secrets")