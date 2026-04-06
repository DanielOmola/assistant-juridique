def preparer_conclusion(texte, llm_client):
    prompt = f"""Rédige des CONCLUSIONS JURIDIQUES structurées:

I. RAPPEL DES FAITS
II. ANALYSE JURIDIQUE
III. ARGUMENTS
IV. CONCLUSION ET PRÉCONISATIONS

Dossier: {texte[:6000]}"""

    system_prompt = "Tu rédiges des conclusions juridiques claires, structurées et argumentées en droit français."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.4)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]