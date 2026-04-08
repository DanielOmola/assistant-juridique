from utils.utils_logging import get_logger

logger = get_logger(__name__)


def simuler_adversaire(case_analysis: str, llm_client) -> str:
    """Simule la stratégie de l’avocat adverse à partir d’une analyse de dossier"""

    logger.info(f"⚔️ Simulation adversaire - {len(case_analysis)} caractères")

    # Vérification des entrées
    if not case_analysis or not case_analysis.strip():
        logger.error("❌ Analyse vide pour simulation adversaire")
        return "❌ Erreur: Aucune analyse disponible"

    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"

    # Preview pour debug
    preview = case_analysis[:200].replace('\n', ' ')
    logger.debug(f"Analyse source: {preview}...")

    prompt = f"""Critique ce dossier et propose une stratégie d’attaque.

Fournis :

1. Failles principales du dossier
2. Arguments adverses clés
3. Stratégie d’attaque recommandée
4. Points faibles à exploiter
5. Risques pour la partie adverse

Analyse :
{case_analysis[:8000]}"""

    system_prompt = "Tu es un avocat adverse expérimenté en droit français."
    
    modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None

    if not modele_actif:
        logger.error("❌ Aucun modèle actif")
        return "❌ Erreur: Aucun modèle actif"
    logger.debug(f"Appel API adversaire - Modèle: {modele_actif}, Température: 0.5")

    try:
        result = llm_client.call_llm(
            prompt,
            system_prompt,
            modele_actif,
            temperature=0.5
        )

        # Vérification du résultat
        if result is None:
            logger.error("❌ Résultat API None")
            return "❌ Erreur: Aucun résultat retourné"

        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return f"❌ Erreur: {result['error']}"

        content = result.get("content", "")
        if not content:
            logger.warning("⚠️ Contenu vide retourné")
            return "⚠️ Aucune analyse adversaire générée"

        # Log de succès
        logger.info(f"✅ Simulation adversaire générée - {len(content)} caractères")
        logger.debug(f"Tokens utilisés: {result.get('tokens', 0)}")
        logger.debug(f"Provider: {result.get('provider', 'inconnu')}")

        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout lors de l'appel API: {str(e)}")
        return "❌ Erreur: Le délai de réponse a été dépassé. Veuillez réessayer."

    except ConnectionError as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion au service."

    except Exception as e:
        logger.error(f"❌ Exception inattendue dans simuler_adversaire: {str(e)}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"