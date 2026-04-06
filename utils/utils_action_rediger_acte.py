def rediger_acte_juridique(texte, llm_client, type_acte="contrat"):
    prompt = f"""Rédige un ACTE JURIDIQUE structuré selon le plan standard suivant :

{get_plan_acte(type_acte)}

À rédiger en langage juridique français, précis, conforme aux articles du Code civil applicables, et adapté aux faits et objectifs suivants :

{texte[:6000]}"""

    system_prompt = f"Tu es un expert en rédaction d'actes juridiques (droit français). Tu rédiges un {type_acte} clair, complet, conforme et exécutoire."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]

def get_plan_acte(type_acte):
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
        "acte_unilatéral": """
I. AUTEUR DE L'ACTE
II. MOTIFS ET EXPOSÉ
III. DISPOSITIONS (obligation, renonciation, reconnaissance, etc.)
IV. DATE – LIEU – SIGNATURE
"""
    }
    return plans.get(type_acte, plans["contrat"])