   
def genere_prompt(prompt_type, texte, templates: dict):
    if templates is None:
        raise ValueError("Le template est None")
    if prompt_type not in templates:
        raise KeyError(f"Type '{prompt_type}' introuvable. Disponibles : {list(templates.keys())}")
    if "prompt" not in templates[prompt_type]:
        raise KeyError(f"Le template '{prompt_type}' ne contient pas de champ 'prompt'")
    
    return templates[prompt_type]["prompt"].replace("{{ text }}", texte).strip()