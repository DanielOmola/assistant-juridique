from utils.utils_logging import get_logger

logger = get_logger(__name__)


# ⚖️ PRÉPARATION D’AUDIENCE
def prepare_audience(case_analysis: str, llm_client) -> str:
    """Génère une stratégie d’audience à partir d’une analyse de dossier"""

    logger.info(f"⚖️ Préparation audience - {len(case_analysis)} caractères")

    # Vérifications
    if not case_analysis or not case_analysis.strip():
        logger.error("❌ Analyse vide fournie pour préparation audience")
        return "❌ Erreur: Aucune analyse disponible"

    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"

    preview = case_analysis[:200].replace('\n', ' ')
    logger.debug(f"Analyse source: {preview}...")

    prompt = f"""
Prépare une stratégie d’audience à partir de cette analyse de dossier.

Fournis :

1. Position à défendre
2. Arguments principaux
3. Arguments secondaires
4. Attaques possibles de l’adversaire
5. Réponses aux attaques
6. Points à marteler à l’audience
7. Pièges à éviter

Analyse :
{case_analysis[:8000]}
"""

    system_prompt = "Tu es un avocat plaidant expérimenté en droit français."
    # modele_actif = llm_client.modele_actif

    # logger.debug(f"Appel API audience - Modèle: {modele_actif}, Température: 0.3")

    try:
        # result = llm_client.call_llm(
        #     prompt,
        #     system_prompt,
        #     modele_actif,
        #     temperature=0.3
        # )
        result = llm_client.call_llm(prompt, system_prompt)

        if result is None:
            logger.error("❌ Résultat API None")
            return "❌ Erreur: Aucun résultat retourné"

        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return f"❌ Erreur: {result['error']}"

        content = result.get("content", "")
        if not content:
            logger.warning("⚠️ Contenu vide retourné")
            return "⚠️ Aucune stratégie générée"

        logger.info(f"✅ Stratégie audience générée - {len(content)} caractères")
        logger.debug(f"Tokens: {result.get('tokens', 0)} | Provider: {result.get('provider', 'inconnu')}")

        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout API: {str(e)}")
        return "❌ Erreur: Délai dépassé"

    except ConnectionError as e:
        logger.error(f"❌ Erreur connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion"

    except Exception as e:
        logger.error(f"❌ Exception audience: {str(e)}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"
