from utils.utils_logging import get_logger

logger = get_logger(__name__)


# ✂️ CHUNKING
def split_text(text: str, chunk_size=2000, overlap=200) -> list:
    """Découpe le texte en chunks"""
    
    if not text:
        logger.warning("⚠️ Texte vide pour split")
        return []

    try:
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap

        logger.info(f"✂️ Texte découpé en {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"❌ Erreur chunking: {str(e)}")
        return []


# 🧠 ANALYSE D'UN CHUNK
def analyze_chunk(chunk: str, llm_client) -> str:
    """Analyse un segment de texte juridique"""

    if not chunk or not chunk.strip():
        logger.warning("⚠️ Chunk vide ignoré")
        return ""

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return ""

    prompt = f"""
Analyse ce passage d'un dossier juridique et extrais :
- faits importants
- éléments juridiques
- points de tension

Texte :
{chunk[:6000]}
"""

    system_prompt = "Tu es un avocat expert en droit français."
    # modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None

    # if not modele_actif:
    #     logger.error("❌ Aucun modèle actif")
    #     return ""

    try:
        # result = llm_client.call_llm(
        #     prompt,
        #     system_prompt,
        #     modele_actif,
        #     temperature=0.3
        # )
        result = llm_client.call_llm(prompt, system_prompt)


        if not result:
            logger.error("❌ Résultat None")
            return ""

        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return ""

        content = result.get("content", "")
        if not content:
            logger.warning("⚠️ Contenu vide retourné")
            
        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout analyse chunk: {str(e)}")
        return ""
    except ConnectionError as e:
        logger.error(f"❌ Erreur connexion: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"❌ Exception analyse chunk: {str(e)}")
        return ""


# 🧩 SYNTHÈSE GLOBALE
def synthesize_analysis(all_chunks_analysis: list, llm_client) -> str:
    """Construit la synthèse globale du dossier"""

    logger.info(f"🧠 Synthèse globale - {len(all_chunks_analysis)} chunks")

    if not all_chunks_analysis:
        logger.error("❌ Aucune analyse à synthétiser")
        return "❌ Erreur: Aucune analyse disponible"

    combined = "\n\n".join([c for c in all_chunks_analysis if c and c.strip()])

    if not combined.strip():
        logger.error("❌ Aucun contenu à synthétiser")
        return "❌ Erreur: Analyse vide"

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return "❌ Erreur: Client LLM non disponible"

    prompt = f"""
À partir des analyses suivantes, construis une synthèse complète du dossier.

Fournis :

1. Résumé global du dossier
2. Chronologie des faits
3. Parties en présence
4. Points juridiques clés
5. Forces du dossier
6. Faiblesses / risques
7. Arguments adverses probables
8. Stratégie recommandée

Analyses :
{combined[:12000]}
"""

    system_prompt = "Tu es un avocat expert en droit français."
    modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None

    if not modele_actif:
        logger.error("❌ Aucun modèle actif")
        return "❌ Erreur: Aucun modèle actif"

    try:
        result = llm_client.call_llm(
            prompt,
            system_prompt,
            modele_actif,
            temperature=0.3
        )

        if not result:
            logger.error("❌ Résultat None")
            return "❌ Erreur: Aucun résultat"

        if result.get("error"):
            logger.error(f"❌ Erreur synthèse: {result['error']}")
            return f"❌ Erreur: {result['error']}"

        content = result.get("content", "")
        
        if not content:
            logger.warning("⚠️ Contenu synthèse vide")
            return "⚠️ Aucune synthèse générée"
        
        logger.info(f"✅ Synthèse générée - {len(content)} caractères")
        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout synthèse: {str(e)}")
        return "❌ Erreur: Délai dépassé"
    except ConnectionError as e:
        logger.error(f"❌ Erreur connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion"
    except Exception as e:
        logger.error(f"❌ Exception synthèse: {str(e)}")
        return f"❌ Erreur: {str(e)}"


# 🚀 ANALYSE COMPLÈTE DOSSIER
def analyse_dossier(textes: list, llm_client) -> str:
    """Analyse un dossier juridique à partir de textes déjà extraits
    
    Args:
        textes: Liste de textes (contenu des documents déjà extraits par l'interface)
        llm_client: Client LLM
    """
    logger.info(f"⚖️ Analyse dossier - {len(textes)} document(s)")

    # Vérifications initiales
    if not textes:
        logger.error("❌ Aucun texte fourni")
        return "❌ Erreur: Aucun texte fourni"

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return "❌ Erreur: Client LLM non disponible"

    try:
        # 1. Concaténer tous les textes (déjà extraits par l'interface)
        all_text = "\n\n".join([t for t in textes if t and t.strip()])

        if not all_text.strip():
            logger.error("❌ Aucun texte valide")
            return "❌ Erreur: Aucun contenu valide"

        logger.info(f"📝 Texte total: {len(all_text)} caractères")

        # 2. Chunking
        chunks = split_text(all_text)

        if not chunks:
            logger.error("❌ Aucun chunk généré")
            return "❌ Erreur: Échec du découpage"

        logger.info(f"📊 {len(chunks)} chunks à analyser")

        # 3. Analyse par chunk
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            logger.info(f"🔍 Analyse chunk {i+1}/{len(chunks)}")
            try:
                analysis = analyze_chunk(chunk, llm_client)
                if analysis and analysis.strip():
                    chunk_analyses.append(analysis)
                else:
                    logger.warning(f"⚠️ Chunk {i+1} analyse vide")
            except Exception as e:
                logger.error(f"❌ Erreur chunk {i+1}: {str(e)}")
                continue

        if not chunk_analyses:
            logger.error("❌ Aucune analyse valide")
            return "❌ Erreur: Analyse des chunks échouée"

        logger.info(f"✅ {len(chunk_analyses)} analyses valides")

        # 4. Synthèse finale
        final_analysis = synthesize_analysis(chunk_analyses, llm_client)

        return final_analysis

    except Exception as e:
        logger.error(f"❌ Exception analyse dossier: {str(e)}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"