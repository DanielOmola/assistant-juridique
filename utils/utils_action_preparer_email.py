def preparer_email(contenu, llm_client):
    prompt = f"""Rédige un email professionnel pour un avocat envoyant ce contenu à son client.

Contenu: {contenu[:2000]}

Structure: Objet, formule d'appel, introduction, corps, conclusion, formule de politesse."""

    system_prompt = "Tu rédiges des emails professionnels pour avocats. Sois clair et courtois."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.4)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]

print("✅ Fonctions IA prêtes avec sélection de modèle")