def ameliorer_redaction(texte, llm_client):
    prompt = f"""Améliore ce texte juridique:
- Style professionnel
- Plus clair et concis
- Corrige les fautes
- Vocabulaire juridique précis

Texte: {texte[:6000]}

Retourne UNIQUEMENT le texte amélioré."""

    system_prompt = "Expert en rédaction juridique française. Améliore le texte sans ajouter de commentaires."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]