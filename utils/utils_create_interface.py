# ============================================
# INTERFACE AVEC LLM_CLIENT CORRIGÉE
# ============================================
from ipywidgets import (
    Textarea, Button, Output, VBox, HBox, HTML,
    FileUpload, Dropdown, Label, Text
)
from IPython.display import display, clear_output, Markdown
import time
import os
from datetime import datetime
import re
from utils.utils_recherche_genial import rechercher_dalloz
# ============================================
# TAMPON AVEC CONFIG YAML
# ============================================
from utils.utils_tampon import (
    charger_config_tampon, 
    sauvegarder_config_tampon, 
    generer_tampon,
    appliquer_tampon,
    appliquer_tampon_fichier  # ← AJOUTER CETTE LIGNE
)

from utils.utils_action_rediger_acte import rediger_acte_juridique


# Style des boutons (taille augmentée)
BUTTON_STYLE = {
    'font_weight': 'bold',
    'padding': '10px 16px',
    'min_width': '140px'
}

def style_button(btn, custom_style=None):
    """Applique un style uniforme aux boutons"""
    style = custom_style or BUTTON_STYLE
    for key, value in style.items():
        setattr(btn, key, value)
    return btn

# ============================================
# WIDGETS TAMPON AVEC CONFIG YAML
# ============================================

def creer_widgets_tampon_config():
    """Crée les widgets pour éditer la configuration du tampon"""
    from ipywidgets import Text, Button, VBox, HBox, HTML, Dropdown
    from utils.utils_tampon import charger_config_tampon, sauvegarder_config_tampon, generer_tampon
    
    config = charger_config_tampon()
    avocat = config["avocat"]
    
    # Champs éditables
    nom = Text(value=avocat["nom"], description="Nom:", layout={'width': '200px'})
    prenom = Text(value=avocat["prenom"], description="Prénom:", layout={'width': '200px'})
    fonction = Text(value=avocat["fonction"], description="Fonction:", layout={'width': '200px'})
    barreau = Text(value=avocat["barreau"], description="Barreau:", layout={'width': '200px'})
    siret = Text(value=avocat["siret"], description="SIRET:", layout={'width': '250px'})
    telephone = Text(value=avocat["telephone"], description="Tél:", layout={'width': '200px'})
    email = Text(value=avocat["email"], description="Email:", layout={'width': '250px'})
    adresse = Text(value=avocat["adresse"], description="Adresse:", layout={'width': '350px'})
    
    # Options
    type_tampon = Dropdown(
        options=[("Officiel", "officiel"), ("Confidentiel", "confidentiel"), 
                 ("Reçu", "recu"), ("Brouillon", "brouillon")],
        value=config["options"]["type_tampon"],
        description="Type:",
        layout={'width': '200px'}
    )
    
    position = Dropdown(
        options=[("Début", "debut"), ("Fin", "fin"), ("Début + Fin", "debut_et_fin")],
        value=config["options"]["position"],
        description="Position:",
        layout={'width': '200px'}
    )
    
    btn_sauvegarder = style_button(Button(description="💾 Sauvegarder config", button_style='primary'))
    btn_tamponner = style_button(Button(description="🖊️ Tamponner", button_style='warning'))
    
    # Aperçu du tampon
    apercu = HTML("")
    
    def mise_a_jour_apercu(*args):
        nouvelle_config = {
            "avocat": {
                "nom": nom.value, "prenom": prenom.value, "fonction": fonction.value,
                "barreau": barreau.value, "siret": siret.value, "telephone": telephone.value,
                "email": email.value, "adresse": adresse.value
            },
            "options": {"type_tampon": type_tampon.value, "position": position.value, "date_format": "%d/%m/%Y"}
        }
        tampon = generer_tampon(nouvelle_config, type_tampon.value)
        apercu.value = f"<pre style='font-size:11px; background:#f5f5f5; padding:8px; border-radius:5px;'>{tampon}</pre>"
    
    # Observer les changements
    for w in [nom, prenom, fonction, barreau, siret, telephone, email, adresse, type_tampon]:
        w.observe(mise_a_jour_apercu, names='value')
    
    def sauvegarder(*args):
        nouvelle_config = {
            "avocat": {
                "nom": nom.value, "prenom": prenom.value, "fonction": fonction.value,
                "barreau": barreau.value, "siret": siret.value, "telephone": telephone.value,
                "email": email.value, "adresse": adresse.value
            },
            "options": {"type_tampon": type_tampon.value, "position": position.value, "date_format": "%d/%m/%Y"}
        }
        sauvegarder_config_tampon(nouvelle_config)
        apercu.value = "<span style='color:green'>✅ Configuration sauvegardée</span>"
    
    btn_sauvegarder.on_click(sauvegarder)
    
    mise_a_jour_apercu()
    
    # Organisation compacte
    widgets = VBox([
        HBox([nom, prenom, fonction]),
        HBox([barreau, siret]),
        HBox([telephone, email]),
        adresse,
        HBox([type_tampon, position, btn_sauvegarder]),
        HTML("<b>📋 Aperçu du tampon :</b>"),
        apercu
    ])
    
    return widgets, btn_tamponner



# Widgets tampon
tampon_widgets, btn_tamponner = creer_widgets_tampon_config()


# ========== FONCTIONS DE SAUVEGARDE ==========
def sanitize_filename(nom: str) -> str:
    """Nettoie un nom de fichier"""
    return re.sub(r'[<>:"/\\|?*]', '_', nom)

def generer_nom_fichier(original: str, suffixe: str) -> str:
    """Génère un nom de fichier par défaut"""
    if original:
        base = os.path.splitext(os.path.basename(original))[0]
        base = sanitize_filename(base)
    else:
        base = "document"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{suffixe}_{timestamp}.txt"

def sauvegarder_texte(contenu: str, chemin_complet: str) -> bool:
    """Sauvegarde du texte dans un fichier"""
    try:
        dossier = os.path.dirname(chemin_complet)
        if dossier and not os.path.exists(dossier):
            os.makedirs(dossier)

        with open(chemin_complet, 'w', encoding='utf-8') as f:
            f.write(contenu)

        print(f"✅ Sauvegardé : {chemin_complet}")
        return True
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return False

# ========== FONCTIONS D'ANALYSE AVEC LLM_CLIENT ==========
def analyser_document(texte: str, llm_client) -> str:
    """Analyse juridique d'un document"""
    prompt = f"""Analyse juridique du document suivant.

Fournis:
1. RÉSUMÉ (5-10 lignes)
2. POINTS CLÉS (liste à puces)
3. RISQUES JURIDIQUES
4. RECOMMANDATIONS

Document: {texte[:6000]}"""

    system_prompt = "Tu es un avocat expert en droit français. Réponds de manière structurée et précise."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]


def preparer_conclusions(texte: str, llm_client) -> str:
    """Prépare des conclusions juridiques"""
    prompt = f"""À partir du document suivant, rédige des CONCLUSIONS JURIDIQUES professionnelles.

Structure:
- RAPPEL DES FAITS (3-5 lignes)
- ANALYSE JURIDIQUE
- ARGUMENTS PRINCIPAUX
- DEMANDES (si applicable)

Document: {texte[:6000]}"""

    system_prompt = "Tu es un avocat plaidant. Rédige des conclusions claires et persuasives."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]

def ameliorer_redaction(texte: str, llm_client) -> str:
    """Améliore la rédaction d'un texte juridique"""
    prompt = f"""Améliore la rédaction de ce texte juridique:

Critères:
- Clarifier le langage
- Corriger les fautes
- Améliorer la structure
- Rendre plus professionnel

TEXTE ORIGINAL:
{texte[:6000]}

TEXTE AMÉLIORÉ:"""

    system_prompt = "Tu es un expert en rédaction juridique française. Améliore le texte sans changer le sens."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]

def preparer_email(analyse: str, llm_client) -> str:
    """Prépare un email professionnel à partir d'une analyse"""
    prompt = f"""Transforme cette analyse juridique en un email professionnel pour un client.

Analyse à transformer:
{analyse[:4000]}

L'email doit inclure:
- Objet clair
- Formule d'appel
- Résumé des points clés
- Prochaines étapes
- Formule de politesse"""

    system_prompt = "Tu es un avocat rédigeant un email à un client. Sois clair, précis et professionnel."

    result = llm_client.call_llm(prompt, system_prompt, llm_client.modele_actif, temperature=0.3)

    if result.get("error"):
        return f"❌ Erreur: {result['error']}"

    return result["content"]

# ========== VÉRIFICATION DES CLÉS API ==========
def get_providers_disponibles(llm_client):
    disponibles = []
    if llm_client.API_KEYS.get("groq"):
        disponibles.append("groq")
    if llm_client.API_KEYS.get("openai"):
        disponibles.append("openai")
    if llm_client.API_KEYS.get("anthropic"):
        disponibles.append("anthropic")
    return disponibles

PROVIDER_TO_CATEGORY = {
    "groq": "🟢 Gratuits (Groq)",
    "openai": "🔵 OpenAI",
    "anthropic": "🟣 Anthropic Claude",
}

# ========== CONSTRUCTION DU DROPDOWN ==========
def creer_selecteur_modele(llm_client):
    """Crée le sélecteur de modèle à partir du LLM client"""
    
    # Récupérer les modèles depuis le client
    provider_models = {}
    for model_id, info in llm_client.MODELES_DISPONIBLES.items():
        provider = info["provider"]
        if provider not in provider_models:
            provider_models[provider] = {}
        provider_models[provider][model_id] = info["name"]
    
    # Construire les choix
    providers_dispo = get_providers_disponibles(llm_client)
    modele_choices = []
    
    for provider in providers_dispo:
        category = PROVIDER_TO_CATEGORY.get(provider, provider)
        models = provider_models.get(provider, {})
        for model_id, model_name in models.items():
            modele_choices.append((f"{category} - {model_name}", model_id))
    
    if not modele_choices:
        modele_choices = [("⚠️ Aucune clé - ajoute dans Secrets", None)]
    
    modele_selector = Dropdown(
        options=modele_choices,
        value=llm_client.modele_actif,
        description="🤖 Modèle:",
        layout={'width': '90%'},
        style={'description_width': 'initial'}
    )
    
    modele_info = HTML("<i>💡 Choisis un modèle selon tes clés API</i>")
    
    def on_modele_change(change):
        selected = change['new']
        if selected is not None:
            llm_client.modele_actif = selected
            info = llm_client.MODELES_DISPONIBLES.get(selected, {})
            modele_info.value = f"<i>📊 Modèle actif: {info.get('name', selected)} | Contexte: {info.get('context', '?')} tokens</i>"
    
    modele_selector.observe(on_modele_change, names='value')
    
    return modele_selector, modele_info



# ========== CRÉATION DE L'INTERFACE ==========
def creer_interface(llm_client):
    """Crée l'interface complète avec le client LLM"""
    
    # Dossier par défaut pour les fichiers externes
    DOSSIER_BASE_EXTERNE = "/content/drive/MyDrive/assistant-juridique"
    
    # Sélecteur de modèle
    modele_selector, modele_info = creer_selecteur_modele(llm_client)


    type_acte_selector = Dropdown(
        options=[
            ("📄 Contrat", "contrat"),
            ("📝 Avenant", "avenant"),
            ("📜 Acte unilatéral", "acte_unilateral"),
            ("🤝 Convention", "convention"),
            ("✅ Quitus", "quitus")
        ],
        value="contrat",
        description="Type d'acte:",
        style={'description_width': 'initial'},
        layout={'width': '300px'}
    )

    btn_rediger_acte = style_button(Button(
        description="📜 Rédiger un acte juridique",
        button_style='primary',
        tooltip="Génère un acte juridique structuré selon le plan standard"
    ))

    def on_rediger_acte(b):
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:red'>❌ Fournissez une description des faits et objectifs</span>"))
            return
        
        type_acte = type_acte_selector.value
        traiter(
            lambda t, c: rediger_acte_juridique(t, c, type_acte), 
            f"📜 Rédaction d'un {type_acte}", 
            texte, 
            f"acte_{type_acte}"
        )
    btn_rediger_acte.on_click(on_rediger_acte)

    # Statut des clés
    status_html = HTML("")
    def mettre_a_jour_status():
        providers = get_providers_disponibles(llm_client)
        if providers:
            status_html.value = f"<span style='color:green'>✅ Clés actives: {', '.join([p.upper() for p in providers])}</span>"
        else:
            status_html.value = "<span style='color:red'>❌ Aucune clé API - ajoute GROQ_API_KEY dans Secrets</span>"
    
    # Variables pour stocker l'état
    dernier_resultat = None
    contenu_fichier_upload = None
    nom_fichier_upload = None
    type_generation_courant = None
    texte_original_courant = None
    fichier_original_path = None  # ← AJOUT OBLIGATOIRE
    
    # Widgets
    label_depot = HTML("<b>📎 Glisse-dépose ton fichier :</b>")
    uploader = FileUpload(
        accept='.txt,.pdf,.docx,.md',
        multiple=False,
        description='📂 Choisir un fichier',
        layout={'width': '100%'}
    )
    status_fichier = HTML("<span style='color:gray'>Aucun fichier</span>")
    
    label_drive = HTML("<b>📁 Ou chemin dans Drive :</b>")
    input_chemin = Textarea(
        placeholder="/content/drive/MyDrive/mon_dossier.pdf",
        layout={'width': '80%', 'height': '50px'}
    )
    
    label_manuel = HTML("<b>✏️ Ou saisis/colle du texte :</b>")
    input_texte = Textarea(
        placeholder="Colle ton texte juridique ici...",
        layout={'width': '100%', 'height': '150px'}
    )
    
    btn_analyser = style_button(Button(description="🔍 Analyser", button_style='primary'))
    btn_conclusions = style_button(Button(description="⚖️ Conclusions", button_style='primary'))
    btn_ameliorer = style_button(Button(description="✨ Améliorer", button_style='primary'))
    btn_email = style_button(Button(description="📧 Email", button_style='info'))
    # ========== AJOUT : Bouton Dalloz manuel ==========
    btn_dalloz = style_button(Button(
                        description="🔍 Dalloz", 
                        button_style='info',
                        tooltip="Rechercher le texte chargé sur Lefebvre Dalloz"
                    ))
    # ========== AJOUT : Bouton pour rechercher le résultat généré ==========
    btn_dalloz_resultat = style_button(Button(
                                description="🔍 Chercher l'analyse sur Dalloz", 
                                button_style='info',
                                layout={'width': 'auto'}
                            ))
    btn_sauvegarder = style_button(Button(description="💾 Sauvegarder résultat", button_style='success'))
    btn_sauvegarder_tout = style_button(Button(description="📦 Sauvegarder tout", button_style='warning'))
    btn_effacer = style_button(Button(description="🗑️ Effacer", button_style='danger'))
    
    # Bouton unique qui détecte automatiquement le type de source
    btn_tamponner = style_button(Button(
                description="🖊️ Tamponner le document",
                button_style='warning',
                tooltip="Applique le tampon (conserve le format PDF/Word/TXT)"
            ))

    output = Output()
    
    # Fonctions utilitaires
    def lire_fichier_upload(content, filename):
        extension = filename.split('.')[-1].lower()
        try:
            if extension == 'txt':
                return content.decode('utf-8')
            elif extension == 'pdf':
                import PyPDF2
                import io
                pdf_file = io.BytesIO(content)
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
            elif extension == 'docx':
                import docx
                import io
                doc_file = io.BytesIO(content)
                doc = docx.Document(doc_file)
                return "\n".join([para.text for para in doc.paragraphs])
            else:
                return f"Format non supporté: {extension}"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def get_texte():
        nonlocal contenu_fichier_upload, fichier_original_path
        
        if input_chemin.value.strip():
            chemin = input_chemin.value.strip()
            if os.path.exists(chemin):
                fichier_original_path = chemin
                with open(chemin, 'rb') as f:
                    return lire_fichier_upload(f.read(), chemin)
            else:
                return None
        elif contenu_fichier_upload:
            return contenu_fichier_upload
        elif input_texte.value.strip():
            fichier_original_path = None
            return input_texte.value
        return None
    
    def traiter(fonction, titre, texte, type_gen):
        nonlocal dernier_resultat, type_generation_courant, texte_original_courant
        
        type_generation_courant = type_gen
        texte_original_courant = texte
        
        with output:
            clear_output(wait=True)
            display(HTML(f"<div style='text-align:center; padding:20px'><b>🤖 {titre} en cours...</b><br><i>Modèle: {llm_client.modele_actif}</i></div>"))
        
        start = time.time()
        try:
            resultat = fonction(texte, llm_client)
            dernier_resultat = resultat
            temps = time.time() - start
            
            with output:
                clear_output(wait=True)
                display(HTML(f"<h3>{titre}</h3>"))
                display(Markdown(resultat))
                display(HTML(f"<small>⚡ Traité en {temps:.1f}s • Modèle: {llm_client.modele_actif}</small>"))
                display(HTML("<hr>"))
                # ========== AJOUT : Afficher Dalloz avec le texte original ==========
                display(HTML("<b>🔍 Recherche juridique complémentaire :</b>"))
                display(rechercher_dalloz(texte))  # ← Recherche à partir du texte source
                # ===================================================================
                display(HTML("<i>💾 Clique sur 'Sauvegarder résultat' pour enregistrer</i>"))
        except Exception as e:
            with output:
                clear_output(wait=True)
                display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
    

    def on_tamponner_texte(b):
        """Tamponne le texte saisi manuellement"""
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:orange'>⚠️ Aucun texte chargé</span>"))
            return
        
        config = charger_config_tampon()
        type_tampon = config["options"].get("type_tampon", "officiel")
        position = config["options"].get("position", "debut")
        
        texte_tamponne = appliquer_tampon(texte, config, type_tampon, position)
        
        with output:
            clear_output(wait=True)
            display(HTML("<h3>🖊️ Texte tamponné</h3>"))
            display(HTML("<pre style='white-space:pre-wrap; font-size:12px; font-family:monospace; background:#f5f5f5; padding:10px; border-radius:5px;'>" + texte_tamponne + "</pre>"))
            
            # Sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chemin = os.path.join(DOSSIER_BASE_EXTERNE, f"texte_tamponne_{timestamp}.txt")
            sauvegarder_texte(texte_tamponne, chemin)

    def on_tamponner_fichier(b):
        """Tamponne le fichier chargé (conserve le format)"""
        
        # Récupérer le chemin du fichier source
        chemin_source = None
        
        if input_chemin.value.strip() and os.path.exists(input_chemin.value.strip()):
            chemin_source = input_chemin.value.strip()
        elif fichier_original_path and os.path.exists(fichier_original_path):
            chemin_source = fichier_original_path
        
        if not chemin_source:
            # Pas de fichier, essayer avec le texte saisi
            texte = get_texte()
            if texte:
                on_tamponner_texte(b)
            else:
                with output:
                    clear_output()
                    display(HTML("<span style='color:orange'>⚠️ Aucun fichier ou texte chargé</span>"))
            return
        
        with output:
            clear_output(wait=True)
            display(HTML(f"<div style='text-align:center; padding:20px'><b>🖊️ Tamponnage en cours...</b><br><i>{os.path.basename(chemin_source)}</i></div>"))
        
        # Appliquer le tampon
        chemin_sortie, erreur = appliquer_tampon_fichier(chemin_source)
        
        if erreur:
            with output:
                clear_output(wait=True)
                display(HTML(f"<span style='color:red'>❌ Erreur: {erreur}</span>"))
            return
        
        with output:
            clear_output(wait=True)
            display(HTML(f"<h3>✅ Document tamponné</h3>"))
            display(HTML(f"<p><strong>Fichier original :</strong> {os.path.basename(chemin_source)}</p>"))
            display(HTML(f"<p><strong>Fichier tamponné :</strong> {os.path.basename(chemin_sortie)}</p>"))
            config_tampon = charger_config_tampon()
            display(HTML(f"<p><strong>Type :</strong> {config_tampon['options']['type_tampon']}</p>"))
            
            # Proposer le téléchargement
            from google.colab import files
            try:
                files.download(chemin_sortie)
                display(HTML("<span style='color:green'>✅ Téléchargement automatique</span>"))
            except:
                display(HTML(f"<a href='{chemin_sortie}' download style='background:#1a73e8; color:white; padding:8px 16px; text-decoration:none; border-radius:5px;'>📥 Télécharger</a>"))


    def on_tamponner(b):
        """Détecte automatiquement si c'est un fichier ou du texte"""
        # Vérifier si un fichier est chargé
        a_un_fichier = False
        
        if input_chemin.value.strip() and os.path.exists(input_chemin.value.strip()):
            a_un_fichier = True
        elif fichier_original_path and os.path.exists(fichier_original_path):
            a_un_fichier = True
        
        if a_un_fichier:
            on_tamponner_fichier(b)
        else:
            on_tamponner_texte(b)

    btn_tamponner.on_click(on_tamponner)

    def on_dalloz_manuel(b):
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:orange'>⚠️ Aucun texte chargé à rechercher</span>"))
            return
        
        with output:
            clear_output(wait=True)
            display(HTML("<b>🔍 Recherche Lefebvre Dalloz</b>"))
            display(rechercher_dalloz(texte))

    def on_dalloz_resultat(b):
        global dernier_resultat
        if not dernier_resultat:
            with output:
                clear_output()
                display(HTML("<span style='color:orange'>⚠️ Générez d'abord une analyse</span>"))
            return
        
        with output:
            clear_output(wait=True)
            display(HTML("<b>🔍 Recherche à partir de l'analyse générée</b>"))
            display(rechercher_dalloz(dernier_resultat))

    btn_dalloz_resultat.on_click(on_dalloz_resultat)

    # Ajouter sous la barre d'outils principale
    # display(HTML("<br>"))
    # display(HBox([btn_dalloz_resultat]))
    # =================================================    

    btn_dalloz.on_click(on_dalloz_manuel)
    # =================================================
    # Gestionnaires d'événements
    def on_upload_change(change):
        nonlocal contenu_fichier_upload, nom_fichier_upload, fichier_original_path
        
        if uploader.value:
            for filename, file_info in uploader.value.items():
                nom_fichier_upload = filename
                fichier_original_path = filename
                content = file_info['content']
                contenu_fichier_upload = lire_fichier_upload(content, filename)
                status_fichier.value = f"<span style='color:green'>✅ {filename} ({len(contenu_fichier_upload)} car)</span>"
                input_texte.value = ""
                input_chemin.value = ""
    
    def on_effacer(b):
        nonlocal contenu_fichier_upload, nom_fichier_upload, dernier_resultat, fichier_original_path
        
        contenu_fichier_upload = None
        nom_fichier_upload = None
        dernier_resultat = None
        fichier_original_path = None
        uploader.value = {}
        input_texte.value = ""
        input_chemin.value = ""
        status_fichier.value = "<span style='color:gray'>Aucun fichier</span>"
        with output:
            clear_output()
            display(HTML("<i>✨ Prêt</i>"))
    
    def on_sauvegarder(b):
        nonlocal dernier_resultat, nom_fichier_upload, type_generation_courant
        
        if not dernier_resultat:
            with output:
                clear_output(wait=True)
                display(HTML("<span style='color:orange'>⚠️ Rien à sauvegarder. Générez d'abord un résultat.</span>"))
            return
        
        # Déterminer le dossier
        if input_chemin.value.strip():
            dossier = os.path.dirname(input_chemin.value.strip())
            nom_base = os.path.basename(input_chemin.value.strip())
        elif nom_fichier_upload:
            dossier = os.path.join(DOSSIER_BASE_EXTERNE, sanitize_filename(nom_fichier_upload.replace('.', '_')))
            nom_base = nom_fichier_upload
        else:
            dossier = DOSSIER_BASE_EXTERNE
            nom_base = "saisie"
        
        os.makedirs(dossier, exist_ok=True)
        nom_fichier = generer_nom_fichier(nom_base, type_generation_courant or "generation")
        chemin_complet = os.path.join(dossier, nom_fichier)
        
        if sauvegarder_texte(dernier_resultat, chemin_complet):
            with output:
                clear_output(wait=True)
                display(HTML(f"<span style='color:green'>✅ Sauvegardé : {chemin_complet}</span>"))
    
    def on_sauvegarder_tout(b):
        nonlocal dernier_resultat, texte_original_courant, nom_fichier_upload, type_generation_courant
        
        if not dernier_resultat or not texte_original_courant:
            with output:
                clear_output(wait=True)
                display(HTML("<span style='color:orange'>⚠️ Générez d'abord un résultat</span>"))
            return
        
        if input_chemin.value.strip():
            dossier_base = os.path.dirname(input_chemin.value.strip())
            nom_base = os.path.basename(input_chemin.value.strip()).replace('.', '_')
        elif nom_fichier_upload:
            dossier_base = os.path.join(DOSSIER_BASE_EXTERNE, sanitize_filename(nom_fichier_upload.replace('.', '_')))
            nom_base = sanitize_filename(nom_fichier_upload.replace('.', '_'))
        else:
            dossier_base = os.path.join(DOSSIER_BASE_EXTERNE, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            nom_base = "saisie"
        
        os.makedirs(dossier_base, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        chemin_original = os.path.join(dossier_base, f"{nom_base}_original_{timestamp}.txt")
        chemin_genere = os.path.join(dossier_base, f"{nom_base}_{type_generation_courant}_{timestamp}.txt")
        
        ok1 = sauvegarder_texte(texte_original_courant, chemin_original)
        ok2 = sauvegarder_texte(dernier_resultat, chemin_genere)
        
        with output:
            clear_output(wait=True)
            if ok1 and ok2:
                display(HTML("<span style='color:green'>✅ Sauvegarde complète réussie !</span>"))
                display(HTML(f"📄 Original : {chemin_original}"))
                display(HTML(f"📄 Généré : {chemin_genere}"))
            else:
                display(HTML("<span style='color:red'>❌ Erreur lors de la sauvegarde</span>"))
    
    def on_analyser(b):
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:red'>❌ Fournissez du texte</span>"))
            return
        traiter(analyser_document, "📄 Analyse du document", texte, "analyse")
    
    def on_conclusions(b):
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:red'>❌ Fournissez du texte</span>"))
            return
        traiter(preparer_conclusions, "⚖️ Conclusions juridiques", texte, "conclusions")
    
    def on_ameliorer(b):
        texte = get_texte()
        if not texte:
            with output:
                clear_output()
                display(HTML("<span style='color:red'>❌ Fournissez du texte</span>"))
            return
        traiter(ameliorer_redaction, "✨ Texte amélioré", texte, "amelioration")
    
    def on_email(b):
        nonlocal dernier_resultat, type_generation_courant
        
        if not dernier_resultat:
            with output:
                clear_output()
                display(HTML("<span style='color:orange'>⚠️ Générez d'abord un résultat</span>"))
            return
        
        with output:
            clear_output(wait=True)
            display(HTML("<b>📧 Génération de l'email...</b>"))
        
        email = preparer_email(dernier_resultat, llm_client)
        dernier_resultat = email
        type_generation_courant = "email"
        
        with output:
            clear_output(wait=True)
            display(HTML("<h3>📧 Email préparé</h3>"))
            display(Markdown(email))
            display(HTML("<hr><i>💾 Clique sur 'Sauvegarder résultat' pour enregistrer</i>"))
    
    # Connecter les événements
    uploader.observe(on_upload_change, names='value')
    btn_analyser.on_click(on_analyser)
    btn_conclusions.on_click(on_conclusions)
    btn_ameliorer.on_click(on_ameliorer)
    btn_email.on_click(on_email)
    btn_sauvegarder.on_click(on_sauvegarder)
    btn_sauvegarder_tout.on_click(on_sauvegarder_tout)
    btn_effacer.on_click(on_effacer)
    
    # Afficher l'interface
    mettre_a_jour_status()
    
    display(HTML("<h1 style='color:#1a73e8'>🤖 Assistant Juridique IA</h1>"))
    display(HTML("<hr>"))
    
    # display(HTML("<h3>🔑 Statut des clés API</h3>"))
    # display(status_html)
    # display(HTML("<br>"))
    
    # display(HTML("<h3>🎛️ Modèle IA</h3>"))
    # display(modele_selector)
    # display(modele_info)
    # display(HTML("<br>"))

# Configuration sur une ligne
    # display(HTML("<h3>⚙️ Configuration</h3>"))
    # display(HBox([
    #     VBox([HTML("<b>🔑 Clés</b>"), status_html]),
    #     VBox([HTML("<b>🤖 Modèle</b>"), modele_selector]),
    #     VBox([HTML("<b>ℹ️ Info</b>"), modele_info])
    # ]))
    # display(HTML("<h3>📎 Fichier</h3>"))
    # display(label_depot)
    # display(uploader)
    # display(status_fichier)
    # display(HTML("<br>"))
    # display(label_drive)
    # display(input_chemin)
       

    
    # # ========== SECTION RÉDACTION D'ACTES ==========
    # display(HTML("<h3>📜 Rédaction d'actes juridiques</h3>"))
    # display(HBox([type_acte_selector, btn_rediger_acte]))
    # display(HTML("<br>"))

    # # Configuration sur une ligne
    # display(HTML("<h3>⚙️ Configuration</h3>"))
    # display(HBox([
    #     VBox([HTML("<b>🔑 Clés</b>"), status_html]),
    #     VBox([HTML("<b>🤖 Modèle</b>"), modele_selector]),
    #     VBox([HTML("<b>ℹ️ Info</b>"), modele_info])
    # ]))
    display(VBox([
        HBox([
            HTML("<b>🔑 Clés</b>", layout={'width': '33%'}),
            HTML("<b>🤖 Modèle</b>", layout={'width': '33%'}),
            HTML("<b>ℹ️ Info</b>", layout={'width': '34%'})
        ]),
        HBox([
            VBox([status_html], layout={'width': '33%'}),
            VBox([modele_selector], layout={'width': '33%'}),
            VBox([modele_info], layout={'width': '34%'})
        ])
    ]))
    
    # Sources sur une ligne
    display(HTML("<h3>📁 Sources</h3>"))
    display(HBox([
        VBox([HTML("<b>📎 Fichier</b>"), uploader, status_fichier], layout={'width': '20%'}),
        VBox([HTML("<b>📁 Drive</b>"), input_chemin], layout={'width': '20%'}),
        VBox([HTML("<b>✏️ Texte</b>"), input_texte], layout={'width': '60%'})
    ]))


    # display(HTML("<br><hr>"))
    # display(HTML("<h3>✏️ Saisie directe</h3>"))
    # display(label_manuel)
    # display(input_texte)

    # Barre d'outils principale
    # display(HBox([btn_analyser, btn_conclusions, btn_ameliorer, btn_email, btn_dalloz]))
    # display(HBox([btn_sauvegarder, btn_sauvegarder_tout, btn_effacer]))
    # ========== SECTION 1 : ANALYSE & RÉDACTION + OUTILS EXTERNES ==========
    display(HBox([
        VBox([
            HTML("<h3 style='margin-top:15px; margin-bottom:5px;'>📊 Analyse & Rédaction</h3>"),
            HBox([btn_analyser, btn_conclusions, btn_ameliorer, btn_email])
        ], layout={'width': '50%'}),
        VBox([
            HTML("<h3 style='margin-top:15px; margin-bottom:5px;'>🔗 Outils Externes</h3>"),
            HBox([btn_dalloz])
        ], layout={'width': '50%', 'align_items': 'flex-start'})
    ]))
    display(HTML("<br>"))
    
    # ========== SECTION 3 : DOCUMENTS ==========
    display(HTML("<h3 style='margin-top:5px; margin-bottom:5px;'>📁 Gestion des documents</h3>"))
    display(HBox([btn_tamponner, btn_sauvegarder, btn_sauvegarder_tout, btn_effacer]))
    display(HTML("<br>"))

    # # ========== SECTION 2 : COMMUNICATION ==========
    # display(HTML("<h3 style='margin-top:5px; margin-bottom:5px;'>📧 Outils Externes</h3>"))
    # display(HBox([btn_dalloz]))
    # display(HTML("<br>"))
    
    
    # # ========== SECTION 4 : UTILITAIRES ==========
    # display(HTML("<h3 style='margin-top:5px; margin-bottom:5px;'>🛠️ Utilitaires</h3>"))
    # display(HBox([btn_effacer]))
    
    display(HTML("<br><hr>"))
    display(HTML("<h3>📋 RÉSULTAT</h3>"))
    display(output)
       
    print("\n✅ Interface prête !")
    print("💡 1. Choisis un modèle")
    print("💡 2. Dépose un fichier ou colle du texte")
    print("💡 3. Clique sur Analyser / Conclusions / Améliorer")
    print("💡 4. Clique sur 'Sauvegarder résultat' pour enregistrer")

# ========== UTILISATION ==========
# Après avoir créé votre LLM client:
# llm_client = LLM_Client(modele_actif, API_KEYS, MODELES_DISPONIBLES)
# 
# Puis lancer l'interface:
# creer_interface(llm_client)