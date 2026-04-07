from utils.utils_logging import get_logger

logger = get_logger(__name__)

def get_plan_acte(type_acte: str) -> str:
    """Retourne le plan standard pour un type d'acte juridique"""
    
    plans = {
        "contrat": """
I. ENTRE LES SOUSSIGNÉS (identité, qualité, domicile)
II. PRÉAMBULE (exposé des motifs et du contexte)
III. OBJET DE L'ACTE
IV. OBLIGATIONS DES PARTIES
V. DURÉE – RENOUVELLEMENT – RÉSILIATION
VI. PRIX – CONDITIONS FINANCIÈRES
VII. GARANTIES – RESPONSABILITÉS
VIII. CLAUSES SPÉCIFIQUES (confidentialité, non-concurrence, force majeure, etc.)
IX. ATTRIBUTION DE JURIDICTION – LOI APPLICABLE
X. SIGNATURES
""",
        "avenant": """
I. PARTIES À L'AVENANT
II. RAPPEL DU CONTRAT INITIAL
III. MODIFICATIONS APPORTÉES
IV. DISPOSITIONS DIVERSES (maintien des autres clauses, entrée en vigueur)
V. SIGNATURES
""",
        "acte_unilateral": """
I. AUTEUR DE L'ACTE
II. MOTIFS ET EXPOSÉ
III. DISPOSITIONS (obligation, renonciation, reconnaissance, etc.)
IV. DATE – LIEU – SIGNATURE
""",
        "convention": """
I. PARTIES CONVENTIONNANTES
II. PRÉAMBULE ET CONTEXTE
III. OBJET DE LA CONVENTION
IV. ENGAGEMENTS RÉCIPROQUES
V. DURÉE ET MODALITÉS
VI. RÉSILIATION – LITIGES
VII. SIGNATURES
""",
        "quitus": """
I. BÉNÉFICIAIRE DU QUITUS
II. OBJET DE LA DÉCHARGE
III. PORTÉE DE LA RENONCIATION
IV. DATE – SIGNATURE
"""
    }
    
    plan = plans.get(type_acte, plans["contrat"])
    logger.debug(f"Plan récupéré pour type_acte: {type_acte} - {len(plan)} caractères")
    return plan

def rediger_acte_juridique(texte: str, llm_client, type_acte: str = "contrat", instructions: str = "") -> str:
    """Rédige un acte juridique structuré selon le plan standard
    
    Args:
        texte: Description des faits et objectifs
        llm_client: Client LLM
        type_acte: Type d'acte à rédiger
        instructions: Instructions spécifiques de l'avocat (clauses particulières, mentions spéciales, etc.)
    """
    
    # Log de début
    logger.info(f"📜 Rédaction d'acte juridique - Type: {type_acte} - {len(texte)} caractères")
    if instructions and instructions.strip():
        logger.info(f"📝 Instructions spécifiques: {instructions[:100]}...")
    
    # Vérification des entrées
    if not texte or not texte.strip():
        logger.error("❌ Texte vide fourni pour la rédaction d'acte")
        return "❌ Erreur: Aucune description des faits et objectifs fournie"
    
    if not llm_client:
        logger.error("❌ Client LLM non initialisé")
        return "❌ Erreur: Client LLM non disponible"
    
    # Vérifier que le type d'acte est valide
    types_valides = ["contrat", "avenant", "acte_unilateral", "convention", "quitus"]
    if type_acte not in types_valides:
        logger.warning(f"⚠️ Type d'acte non standard: {type_acte}, utilisation du contrat par défaut")
        type_acte = "contrat"
    
    # Preview pour le log
    texte_preview = texte[:200].replace('\n', ' ')
    logger.debug(f"Description des faits: {texte_preview}...")
    
    # Récupérer le plan
    plan = get_plan_acte(type_acte)
    logger.debug(f"Plan utilisé: {plan[:200]}...")
    
    # Construire le prompt avec les instructions si fournies
    instructions_section = ""
    if instructions and instructions.strip():
        instructions_section = f"""
INSTRUCTIONS SPÉCIFIQUES DE L'AVOCAT :
{instructions.strip()}

IMPORTANT : Veillez à intégrer ces instructions dans la rédaction de l'acte (clauses spécifiques, mentions particulières, adaptations selon les besoins du client).
"""
    
    prompt = f"""Rédige un ACTE JURIDIQUE structuré selon le plan standard suivant :

{plan}
{instructions_section}

À rédiger en langage juridique français, précis, conforme aux articles du Code civil applicables, et adapté aux faits et objectifs suivants :

{texte[:6000]}"""

    system_prompt = f"Tu es un expert en rédaction d'actes juridiques (droit français). Tu rédiges un {type_acte} clair, complet, conforme et exécutoire."
    modele_actif = llm_client.modele_actif
    
    logger.debug(f"Appel API - Modèle: {modele_actif}, Température: 0.3")
    
    try:
        result = llm_client.call_llm(prompt, system_prompt, modele_actif, temperature=0.3)

        # Vérification du résultat
        if result is None:
            logger.error("❌ Résultat API None")
            return "❌ Erreur: La requête n'a pas retourné de résultat"
        
        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return f"❌ Erreur: {result['error']}"
        
        if not result.get("content"):
            logger.warning("⚠️ Contenu vide retourné par l'API")
            return f"⚠️ Aucun {type_acte} généré. Veuillez réessayer."
        
        # Vérification basique de la structure (présence des sections principales)
        contenu = result["content"]
        sections_trouvees = []
        for section in ["I.", "II.", "III.", "IV.", "V."]:
            if section in contenu[:500]:  # Vérifier dans les 500 premiers caractères
                sections_trouvees.append(section)
        
        # Log de succès
        logger.info(f"✅ Acte {type_acte} rédigé - {len(contenu)} caractères")
        logger.debug(f"Sections trouvées: {', '.join(sections_trouvees)}")
        logger.debug(f"Tokens utilisés: {result.get('tokens', 0)}")
        logger.debug(f"Provider: {result.get('provider', 'inconnu')}")
        
        # Avertissement si structure incomplète
        if len(sections_trouvees) < 3:
            logger.warning(f"⚠️ Structure de l'acte potentiellement incomplète - Sections trouvées: {len(sections_trouvees)}/5")
        
        return contenu
        
    except TimeoutError as e:
        logger.error(f"❌ Timeout lors de l'appel API: {str(e)}")
        return "❌ Erreur: Le délai de réponse a été dépassé. Veuillez réessayer."
        
    except ConnectionError as e:
        logger.error(f"❌ Erreur de connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion au service. Vérifiez votre réseau."
        
    except Exception as e:
        logger.error(f"❌ Exception inattendue dans rediger_acte_juridique: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"