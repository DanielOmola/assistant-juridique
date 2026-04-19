from utils.utils_logging import get_logger

logger = get_logger(__name__)

def preparer_conclusion(texte: str, llm_client) -> str:
    """Rédige des conclusions juridiques structurées"""
    
    # Log de début
    logger.info(f"⚖️ Génération de conclusions - {len(texte)} caractères")
    
    # Vérification des entrées
    if not texte or not texte.strip():
        logger.error("❌ Texte vide fourni pour la génération de conclusions")
        return "❌ Erreur: Aucun texte à analyser"
    
    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"
    
    # Preview pour le log
    texte_preview = texte[:200].replace('\n', ' ')
    logger.debug(f"Texte source: {texte_preview}...")
    
    prompt = f"""Rédige des CONCLUSIONS JURIDIQUES structurées:
                    I. RAPPEL DES FAITS
                    II. ANALYSE JURIDIQUE
                    III. ARGUMENTS
                    IV. CONCLUSION ET PRÉCONISATIONS

                    Dossier: {texte[:6000]}
            """

    system_prompt = "Tu rédiges des conclusions juridiques claires, structurées et argumentées en droit français."
    # modele_actif = llm_client.modele_actif
    
    # logger.debug(f"Appel API - Modèle: {modele_actif}, Température: 0.4")
    
    try:
        # result = llm_client.call_llm(prompt, system_prompt, modele_actif, temperature=0.4)
        result = llm_client.call_llm(prompt, system_prompt)
        # Vérification du résultat
        if result is None:
            logger.error("❌ Résultat API None")
            return "❌ Erreur: La requête n'a pas retourné de résultat"
        
        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return f"❌ Erreur: {result['error']}"
        
        if not result.get("content"):
            logger.warning("⚠️ Contenu vide retourné par l'API")
            return "⚠️ Aucune conclusion générée. Veuillez réessayer."
        
        # Log de succès
        logger.info(f"✅ Conclusions générées - {len(result['content'])} caractères")
        logger.debug(f"Tokens utilisés: {result.get('tokens', 0)}")
        logger.debug(f"Provider: {result.get('provider', 'inconnu')}")
        
        return result["content"]
        
    except TimeoutError as e:
        logger.error(f"❌ Timeout lors de l'appel API: {str(e)}")
        return "❌ Erreur: Le délai de réponse a été dépassé. Veuillez réessayer."
        
    except ConnectionError as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion au service. Vérifiez votre réseau."
        
    except Exception as e:
        logger.error(f"❌ Exception inattendue dans preparer_conclusion: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"