from utils.utils_logging import get_logger

logger = get_logger(__name__)

def ameliorer_redaction(texte: str, llm_client) -> str:
    """Améliore la rédaction d'un texte juridique"""
    
    # Log de début
    logger.info(f"✨ Amélioration de rédaction - {len(texte)} caractères")
    
    # Vérification des entrées
    if not texte or not texte.strip():
        logger.error("❌ Texte vide fourni pour l'amélioration")
        return "❌ Erreur: Aucun texte à améliorer"
    
    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"
    
    # Preview pour le log
    texte_preview = texte[:200].replace('\n', ' ')
    logger.debug(f"Texte original: {texte_preview}...")
    
    prompt = f"""Améliore ce texte juridique:
- Style professionnel
- Plus clair et concis
- Corrige les fautes
- Vocabulaire juridique précis

Texte: {texte[:6000]}

Retourne UNIQUEMENT le texte amélioré."""

    system_prompt = "Expert en rédaction juridique française. Améliore le texte sans ajouter de commentaires."
    # modele_actif = llm_client.modele_actif
    
    # logger.debug(f"Appel API - Modèle: {modele_actif}, Température: 0.3")
    
    try:
        # result = llm_client.call_llm(prompt, system_prompt, modele_actif, temperature=0.3)
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
            return "⚠️ Aucune amélioration générée. Veuillez réessayer."
        
        # Calculer le taux d'amélioration approximatif
        original_len = len(texte)
        new_len = len(result["content"])
        ratio = (1 - new_len/original_len) * 100 if original_len > 0 else 0
        
        # Log de succès
        logger.info(f"✅ Texte amélioré - Original: {original_len} → Nouveau: {new_len} caractères ({ratio:.0f}% de changement)")
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
        logger.error(f"❌ Exception inattendue dans ameliorer_redaction: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"