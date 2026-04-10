   
def genere_prompt(prompt_type, texte, template: dict):
    if template is None:
        raise ValueError("Le template est None")
    if prompt_type not in template:
        raise KeyError(f"Type '{prompt_type}' introuvable. Disponibles : {list(template.keys())}")
    if "prompt" not in template[prompt_type]:
        raise KeyError(f"Le template '{prompt_type}' ne contient pas de champ 'prompt'")
    
    return template[prompt_type]["prompt"].replace("{{ text }}", texte).strip()