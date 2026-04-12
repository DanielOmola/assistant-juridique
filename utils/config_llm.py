from google.colab import userdata

# def get_api_keys():
#     # ========== LISTE DES CLÉS API ATTENDUES ==========
#     # Correspondance entre les noms dans Secrets et les noms utilisés dans le code
#     PROVIDER_KEY_MAPPING = {
#         "GROQ_API_KEY": "groq",
#         "OPENAI_API_KEY": "openai",  # Note: corrigé (toi tu avais OPENAIP_API_KEY avec un P en trop)
#         "ANTHROPIC_API_KEY": "anthropic",
#         "MISTRAL_API_KEY": "mistral",
#         "GOOGLE_API_KEY": "google",
#     }

#     # ========== CHARGEMENT DES CLÉS API ==========
#     API_KEYS = {
#         "openai": None,
#         "anthropic": None,
#         "groq": None,
#         "mistral": None,
#         "google": None,
#     }

#     print("🔑 Chargement des clés API...")
#     for secret_name, provider_name in PROVIDER_KEY_MAPPING.items():
#         try:
#             test_key = userdata.get(secret_name)
#             if test_key and "n/a" not in test_key.lower():
#                 API_KEYS[provider_name] = test_key
#                 print(f"✅ {secret_name} → {provider_name}: {test_key[:10]}... (caché)")
#             else:
#                 print(f"⚠️ {secret_name}: clé vide ou non configurée")
#         except Exception as e:
#             print(f"❌ {secret_name}: non trouvée - {str(e)}")
#     return API_KEYS


def get_api_keys():
    # ========== LISTE DES CLÉS API ATTENDUES ==========
    # Correspondance entre les noms dans Secrets et les noms utilisés dans le code
    PROVIDER_KEY_MAPPING = {
        "GROQ_API_KEY": "groq",
        "OPENAI_API_KEY": "openai",  # Note: corrigé (toi tu avais OPENAIP_API_KEY avec un P en trop)
        "ANTHROPIC_API_KEY": "anthropic",
        "MISTRAL_API_KEY": "mistral",
        "GOOGLE_API_KEY": "google",
    }

    # ========== CHARGEMENT DES CLÉS API ==========
    API_KEYS = {
        "openai": None,
        "anthropic": None,
        "groq": None,
        "mistral": None,
        "google": None,
    }

    print("🔑 Chargement des clés API...")
    for secret_name, provider_name in PROVIDER_KEY_MAPPING.items():
        try:
            test_key = userdata.get(secret_name)
            if test_key and "n/a" not in test_key.lower():
                API_KEYS[provider_name] = test_key
                print(f"✅ {secret_name} → {provider_name}: {test_key[:10]}... (caché)")
            else:
                print(f"⚠️ {secret_name}: clé vide ou non configurée")
        except Exception as e:
            print(f"❌ {secret_name}: non trouvée - {str(e)}")
    return API_KEYS

def get_llm_config(api_keys):
    """
    Détermine le modèle actif par défaut en fonction des clés API disponibles.
    
    Args:
        api_keys (dict): Dictionnaire contenant les clés API pour différents providers
                         Exemple: {"groq": "clé_groq", "openai": "clé_openai"}
    
    Returns:
        tuple: (modele_actif, message_info)
    """
    MODELES_DISPONIBLES = {
        # OpenAI
        # https://developers.openai.com/api/docs
        "gpt-5.4": {"provider": "openai", "name": "GPT-5.4 (recommandé)", "context": 1050000},
        "gpt-5.4-mini": {"provider": "openai", "name": "GPT-5.4 mini", "context": 400000},
        "gpt-5.4-nano": {"provider": "openai", "name": "GPT-5.4 nano (rapide/peu cher)", "context": 400000},


        # Anthropic Claude
        # https://platform.claude.com/docs/en/about-claude/models/overview
        "claude-opus-4-6": {"provider": "anthropic", "name": "Claude Opus 4.6 (meilleur juridique)", "context": 1000000},
        "claude-sonnet-4-6": {"provider": "anthropic", "name": "Claude Sonnet 4.6 (très précis)", "context": 1000000},
        "claude-haiku-4-5-20251001": {"provider": "anthropic", "name": "Claude Haiku 4.5 (rapide)", "context": 200000},

        # Groq (modèles gratuits/rapides)
        # https://console.groq.com/docs/models
        "llama-3.3-70b-versatile": {"provider": "groq", "name": "Llama 3.3 70B (gratuit/rapide)", "context": 131072},
        "llama-3.1-8b-instant": {"provider": "groq", "name": "Llama 3.1 8B", "context": 131072},
        "openai/gpt-oss-120b": {"provider": "groq", "name": "GPT OSS 120B", "context": 131072},
        "openai/gpt-oss-20b": {"provider": "groq", "name": "GPT OSS 20B", "context": 131072},

        # https://ai.google.dev/gemini-api/docs/models?hl=fr
        "gemini-3.1-pro-preview": {"provider": "google", "name": "Gemini 3.1 Pro (preview)", "context": 1048576},
        "gemini-3-flash-preview": {"provider": "google", "name": "Gemini 3 Flash", "context": 131072},
        "gemini-3.1-flash-lite-preview": {"provider": "google", "name": "Gemini 3.1 Flash-Lite Preview", "context": 131072},
    }
    
    # Modèle par défaut (utilise GROQ qui est gratuit si dispo)
    if api_keys.get("groq"):
        modele_actif = "llama-3.3-70b-versatile"
        message = f"\n🎯 Modèle par défaut: {modele_actif} (Groq - gratuit)"
    elif api_keys.get("openai"):
        modele_actif = "gpt-3.5-turbo"
        message = f"\n🎯 Modèle par défaut: {modele_actif} (OpenAI)"
    else:
        modele_actif = "llama-3.3-70b-versatile"
        message = f"\n⚠️ Aucune clé valide trouvée. Ajoute une clé dans les Secrets (🔑)"
    
    return modele_actif, message, MODELES_DISPONIBLES

def get_modele_actif():
    API_KEYS = get_api_keys()
    # print(f'\n{"="*25} API_KEYS {"="*25}\n\t{API_KEYS}')
    modele_actif, message, MODELES_DISPONIBLES = get_llm_config(api_keys=API_KEYS)
    # print(f'\n{"="*25} modele_actif {"="*25}\n\t{modele_actif}')
    return modele_actif, message, MODELES_DISPONIBLES, API_KEYS

# Exemple d'utilisation :
# API_KEYS = {"groq": "votre_clé_groq", "openai": None, "anthropic": None}
# modele_actif, message, modeles = get_modele_actif(API_KEYS)
# print(message)