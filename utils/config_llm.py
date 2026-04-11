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
        "gpt-4o": {"provider": "openai", "name": "GPT-4o (recommandé)", "context": 128000},
        "gpt-4-turbo": {"provider": "openai", "name": "GPT-4 Turbo", "context": 128000},
        "gpt-3.5-turbo": {"provider": "openai", "name": "GPT-3.5 Turbo (rapide/peu cher)", "context": 16385},

        # Anthropic Claude
        "claude-3-5-sonnet-20241022": {"provider": "anthropic", "name": "Claude 3.5 Sonnet (meilleur juridique)", "context": 200000},
        "claude-3-opus-20240229": {"provider": "anthropic", "name": "Claude 3 Opus (très précis)", "context": 200000},
        "claude-3-haiku-20240307": {"provider": "anthropic", "name": "Claude 3 Haiku (rapide)", "context": 200000},

        # Groq (modèles gratuits/rapides)
        "llama-3.3-70b-versatile": {"provider": "groq", "name": "Llama 3.3 70B (gratuit/rapide)", "context": 128000},
        "mixtral-8x7b-32768": {"provider": "groq", "name": "Mixtral 8x7B (gratuit)", "context": 32768},
        "gemma2-9b-it": {"provider": "groq", "name": "Gemma 2 9B (gratuit)", "context": 8192},
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