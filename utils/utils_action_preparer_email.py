from utils.utils_logging import get_logger

logger = get_logger(__name__)

def preparer_email(contenu: str, llm_client) -> str:
    """Rédige un email professionnel pour un avocat à destination de son client"""
    
    # Log de début
    logger.info(f"📧 Génération d'email - {len(contenu)} caractères")
    
    # Vérification des entrées
    if not contenu or not contenu.strip():
        logger.error("❌ Contenu vide fourni pour la génération d'email")
        return "❌ Erreur: Aucun contenu pour générer l'email"
    
    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"
    
    # Preview pour le log
    contenu_preview = contenu[:200].replace('\n', ' ')
    logger.debug(f"Contenu source: {contenu_preview}...")
    
    prompt = f"""Rédige un email professionnel pour un avocat envoyant ce contenu à son client.

Contenu: {contenu[:2000]}

Structure: Objet, formule d'appel, introduction, corps, conclusion, formule de politesse."""

    system_prompt = "Tu rédiges des emails professionnels pour avocats. Sois clair et courtois."
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
            return "⚠️ Aucun email généré. Veuillez réessayer."
        
        # Extraire l'objet pour le log (première ligne)
        email_content = result["content"]
        objet = email_content.split('\n')[0] if email_content else "Non trouvé"
        objet = objet.replace('Objet:', '').strip()[:50]
        
        # Log de succès
        logger.info(f"✅ Email généré - {len(email_content)} caractères")
        logger.debug(f"Objet détecté: {objet}")
        logger.debug(f"Tokens utilisés: {result.get('tokens', 0)}")
        logger.debug(f"Provider: {result.get('provider', 'inconnu')}")
        
        return email_content
        
    except TimeoutError as e:
        logger.error(f"❌ Timeout lors de l'appel API: {str(e)}")
        return "❌ Erreur: Le délai de réponse a été dépassé. Veuillez réessayer."
        
    except ConnectionError as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion au service. Vérifiez votre réseau."
        
    except Exception as e:
        logger.error(f"❌ Exception inattendue dans preparer_email: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"

print("✅ Fonctions IA prêtes avec sélection de modèle")