from utils.utils_logging import get_logger

logger = get_logger(__name__)

def analyser_document(texte: str, llm_client) -> str:
    """Analyse juridique d'un document"""
    
    # Log de début
    logger.info(f"📄 Analyse demandée - {len(texte)} caractères")
    
    # Troncature pour le log (éviter de polluer)
    texte_preview = texte[:200].replace('\n', ' ')
    logger.debug(f"Texte à analyser: {texte_preview}...")
    
    prompt = f"""Analyse juridique du document suivant.

Fournis:
1. RÉSUMÉ (5-10 lignes)
2. POINTS CLÉS (liste à puces)
3. RISQUES JURIDIQUES
4. RECOMMANDATIONS

Document: {texte[:6000]}"""

    system_prompt = "Tu es un avocat expert en droit français. Réponds de manière structurée et précise."
    modele_actif = llm_client.modele_actif
    
    logger.debug(f"Appel API - Modèle: {modele_actif}, Température: 0.3")
    
    try:
        result = llm_client.call_llm(prompt, system_prompt, modele_actif, temperature=0.3)

        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return f"❌ Erreur: {result['error']}"
        
        logger.info(f"✅ Analyse réussie - {len(result['content'])} caractères")
        logger.debug(f"Tokens utilisés: {result.get('tokens', 0)}")
        logger.debug(f"Provider: {result.get('provider', 'inconnu')}")
        
        return result["content"]
        
    except Exception as e:
        logger.error(f"❌ Exception dans analyser_document: {str(e)}")
        raise