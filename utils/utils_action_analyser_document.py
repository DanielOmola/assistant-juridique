def analyser_document(texte, llm_client):
    prompt = f"""Analyse juridique du document suivant.

Fournis:
1. RÉSUMÉ (5-10 lignes)
2. POINTS CLÉS (liste à puces)
3. RISQUES JURIDIQUES
4. RECOMMANDATIONS

Document: {texte[:6000]}"""

    system_prompt = "Tu es un avocat expert en droit français. Réponds de manière structurée et précise."
    modele_actif = llm_client.modele_actif
    result = llm_client.call_llm(prompt, system_prompt, modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]