# ============================================
# CSS STYLES
# ============================================
from IPython.display import HTML

display(HTML("""
<style>
/* Global */
.widget-label { font-weight: bold !important; }
button { border-radius: 8px !important; transition: all 0.2s ease; }

/* Sections */
.section-box {
    background: #f9fafc;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #e0e0e0;
}

/* Titles */
.section-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #1a73e8;
}

/* Result box */
.output-box {
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
}

/* Buttons spacing */
.widget-button {
    margin-right: 8px !important;
}

/* Hover */
button:hover {
    opacity: 0.85;
    transform: translateY(-1px);
}
</style>
"""))

# ============================================
# IMPORTS
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
from utils.utils_tampon import (
    charger_config_tampon, 
    sauvegarder_config_tampon, 
    generer_tampon,
    appliquer_tampon,
    appliquer_tampon_fichier
)
from utils.utils_action_rediger_acte import rediger_acte_juridique


# ============================================
# CONSTANTES & STYLES
# ============================================
BUTTON_STYLE = {
    'font_weight': 'bold',
    'padding': '10px 16px',
    'min_width': '140px'
}

def style_button(btn, custom_style=None):
    style = custom_style or BUTTON_STYLE
    for key, value in style.items():
        setattr(btn, key, value)
    return btn


# ============================================
# STATE MANAGEMENT
# ============================================
class AppState:
    def __init__(self):
        self.dernier_resultat = None
        self.texte_original = None
        self.type_generation = None
        self.fichier_path = None
        self.contenu_upload = None
        self.nom_fichier = None
        self.llm_client = None

state = AppState()


# ============================================
# FONCTIONS MÉTIER
# ============================================
def sanitize_filename(nom: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', nom)

def generer_nom_fichier(original: str, suffixe: str) -> str:
    if original:
        base = os.path.splitext(os.path.basename(original))[0]
        base = sanitize_filename(base)
    else:
        base = "document"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{suffixe}_{timestamp}.txt"

def sauvegarder_texte(contenu: str, chemin_complet: str) -> bool:
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


# ============================================
# FONCTIONS D'ANALYSE
# ============================================
def analyser_document(texte: str, llm_client) -> str:
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


# ============================================
# WIDGETS TAMPON
# ============================================
def creer_widgets_tampon_config():
    from ipywidgets import Text, Button, VBox, HBox, HTML, Dropdown
    from utils.utils_tampon import charger_config_tampon, sauvegarder_config_tampon, generer_tampon
    
    config = charger_config_tampon()
    avocat = config["avocat"]
    
    nom = Text(value=avocat["nom"], description="Nom:", layout={'width': '200px'})
    prenom = Text(value=avocat["prenom"], description="Prénom:", layout={'width': '200px'})
    fonction = Text(value=avocat["fonction"], description="Fonction:", layout={'width': '200px'})
    barreau = Text(value=avocat["barreau"], description="Barreau:", layout={'width': '200px'})
    siret = Text(value=avocat["siret"], description="SIRET:", layout={'width': '250px'})
    telephone = Text(value=avocat["telephone"], description="Tél:", layout={'width': '200px'})
    email = Text(value=avocat["email"], description="Email:", layout={'width': '250px'})
    adresse = Text(value=avocat["adresse"], description="Adresse:", layout={'width': '350px'})
    
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

tampon_widgets, btn_tamponner = creer_widgets_tampon_config()


# ============================================
# VÉRIFICATION DES CLÉS API
# ============================================
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

def creer_selecteur_modele(llm_client):
    provider_models = {}
    for model_id, info in llm_client.MODELES_DISPONIBLES.items():
        provider = info["provider"]
        if provider not in provider_models:
            provider_models[provider] = {}
        provider_models[provider][model_id] = info["name"]
    
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
        layout={'width': '100%'},
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


# ============================================
# INTERFACE PRINCIPALE
# ============================================
class AssistantUI:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.modele_selector, self.modele_info = creer_selecteur_modele(llm_client)
        self.build_ui()
        self.bind_events()

    def build_ui(self):
        # Widgets d'entrée
        self.input_texte = Textarea(
            placeholder="Colle ton texte juridique ici...",
            layout={'width': '100%', 'height': '120px'}
        )
        
        self.uploader = FileUpload(
            accept='.txt,.pdf,.docx,.md',
            multiple=False,
            description='📂 Choisir un fichier',
            layout={'width': '100%'}
        )
        self.status_file = HTML("📎 Aucun fichier")
        
        self.input_chemin = Textarea(
            placeholder="/content/drive/MyDrive/mon_dossier.pdf",
            layout={'width': '100%', 'height': '60px'}
        )
        
        # Type d'acte
        self.type_acte_selector = Dropdown(
            options=[
                ("📄 Contrat", "contrat"),
                ("📝 Avenant", "avenant"),
                ("📜 Acte unilatéral", "acte_unilateral"),
                ("🤝 Convention", "convention"),
                ("✅ Quitus", "quitus")
            ],
            value="contrat",
            description="Type:",
            layout={'width': '200px'}
        )
        
        # Boutons
        self.btn_analyser = style_button(Button(description="🔍 Analyser", button_style='primary'))
        self.btn_conclusions = style_button(Button(description="⚖️ Conclusions", button_style='primary'))
        self.btn_ameliorer = style_button(Button(description="✨ Améliorer", button_style='primary'))
        self.btn_rediger_acte = style_button(Button(description="📜 Rédiger acte", button_style='primary'))
        self.btn_email = style_button(Button(description="📧 Email", button_style='info'))
        self.btn_dalloz = style_button(Button(description="🔍 Dalloz", button_style='info'))
        self.btn_tamponner = btn_tamponner
        self.btn_sauvegarder = style_button(Button(description="💾 Sauvegarder", button_style='success'))
        self.btn_sauvegarder_tout = style_button(Button(description="📦 Sauvegarder tout", button_style='warning'))
        self.btn_effacer = style_button(Button(description="🗑️ Effacer", button_style='danger'))
        
        self.output = Output()
        
        # Statut des clés
        self.status_html = HTML("")
        self.mettre_a_jour_status()

    def mettre_a_jour_status(self):
        providers = get_providers_disponibles(self.llm)
        if providers:
            self.status_html.value = f"<span style='color:green'>✅ {', '.join([p.upper() for p in providers])}</span>"
        else:
            self.status_html.value = "<span style='color:red'>❌ Aucune clé API</span>"

    def get_texte(self):
        if self.input_chemin.value.strip():
            chemin = self.input_chemin.value.strip()
            if os.path.exists(chemin):
                with open(chemin, 'rb') as f:
                    return self.lire_fichier_upload(f.read(), chemin)
            return None
        elif hasattr(self, 'contenu_upload') and self.contenu_upload:
            return self.contenu_upload
        elif self.input_texte.value.strip():
            return self.input_texte.value
        return None

    def lire_fichier_upload(self, content, filename):
        extension = filename.split('.')[-1].lower()
        try:
            if extension == 'txt':
                return content.decode('utf-8')
            elif extension == 'pdf':
                import PyPDF2, io
                pdf_file = io.BytesIO(content)
                reader = PyPDF2.PdfReader(pdf_file)
                return "\n".join([page.extract_text() for page in reader.pages])
            elif extension == 'docx':
                import docx, io
                doc_file = io.BytesIO(content)
                doc = docx.Document(doc_file)
                return "\n".join([para.text for para in doc.paragraphs])
            else:
                return f"Format non supporté: {extension}"
        except Exception as e:
            return f"Erreur: {str(e)}"

    def traiter(self, fonction, titre, texte, type_gen):
        state.type_generation = type_gen
        state.texte_original = texte
        
        with self.output:
            clear_output(wait=True)
            display(HTML(f"<div class='output-box' style='text-align:center'><b>🤖 {titre} en cours...</b><br><i>Modèle: {self.llm.modele_actif}</i></div>"))
        
        start = time.time()
        try:
            resultat = fonction(texte, self.llm)
            state.dernier_resultat = resultat
            temps = time.time() - start
            
            with self.output:
                clear_output(wait=True)
                display(HTML(f"<h3>{titre}</h3>"))
                display(Markdown(resultat))
                display(HTML(f"<small>⚡ {temps:.1f}s • Modèle: {self.llm.modele_actif}</small>"))
                display(HTML("<hr>"))
                display(HTML("<b>🔍 Recherche juridique complémentaire :</b>"))
                display(rechercher_dalloz(texte))
                display(HTML("<i>💾 Sauvegarde disponible ci-dessous</i>"))
        except Exception as e:
            with self.output:
                clear_output(wait=True)
                display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))

    def on_upload_change(self, change):
        if self.uploader.value:
            for filename, file_info in self.uploader.value.items():
                self.nom_fichier = filename
                content = file_info['content']
                self.contenu_upload = self.lire_fichier_upload(content, filename)
                self.status_file.value = f"✅ {filename} ({len(self.contenu_upload)} car)"
                self.input_texte.value = ""
                self.input_chemin.value = ""

    def on_effacer(self, b):
        self.contenu_upload = None
        self.nom_fichier = None
        state.dernier_resultat = None
        self.uploader.value = {}
        self.input_texte.value = ""
        self.input_chemin.value = ""
        self.status_file.value = "📎 Aucun fichier"
        with self.output:
            clear_output()
            display(HTML("<i>✨ Prêt</i>"))

    def on_sauvegarder(self, b):
        if not state.dernier_resultat:
            with self.output:
                clear_output(wait=True)
                display(HTML("<span style='color:orange'>⚠️ Rien à sauvegarder</span>"))
            return
        
        base = self.nom_fichier or "document"
        chemin = os.path.join("/content/drive/MyDrive/assistant-juridique", 
                              generer_nom_fichier(base, state.type_generation or "generation"))
        if sauvegarder_texte(state.dernier_resultat, chemin):
            with self.output:
                clear_output(wait=True)
                display(HTML(f"<span style='color:green'>✅ Sauvegardé : {chemin}</span>"))

    def bind_events(self):
        self.uploader.observe(self.on_upload_change, names='value')
        self.btn_analyser.on_click(lambda b: self.traiter(analyser_document, "📄 Analyse", self.get_texte(), "analyse"))
        self.btn_conclusions.on_click(lambda b: self.traiter(preparer_conclusions, "⚖️ Conclusions", self.get_texte(), "conclusions"))
        self.btn_ameliorer.on_click(lambda b: self.traiter(ameliorer_redaction, "✨ Amélioration", self.get_texte(), "amelioration"))
        self.btn_rediger_acte.on_click(lambda b: self.traiter(
            lambda t, c: rediger_acte_juridique(t, c, self.type_acte_selector.value),
            f"📜 {self.type_acte_selector.value}", self.get_texte(), "acte"))
        self.btn_email.on_click(lambda b: self.traiter(preparer_email, "📧 Email", state.dernier_resultat or self.get_texte(), "email"))
        self.btn_dalloz.on_click(lambda b: self.traiter(lambda t, c: rechercher_dalloz(t), "🔍 Dalloz", self.get_texte(), "dalloz"))
        self.btn_sauvegarder.on_click(self.on_sauvegarder)
        self.btn_effacer.on_click(self.on_effacer)

    def render(self):
        display(HTML("<h1 style='color:#1a73e8; text-align:center'>⚖️ Juribot</h1>"))
        display(HTML("<p style='text-align:center'><i>Prêt à vous libérer du temps</i></p>"))
        display(HTML("<hr>"))
        
        # Ligne 1 : Configuration
        display(HTML("<div class='section-box'>"))
        display(HTML("<div class='section-title'>⚙️ Configuration</div>"))
        display(HBox([
            VBox([HTML("<b>🔑 Clés</b>"), self.status_html], layout={'width': '25%'}),
            VBox([HTML("<b>🤖 Modèle</b>"), self.modele_selector], layout={'width': '50%'}),
            VBox([HTML("<b>ℹ️ Info</b>"), self.modele_info], layout={'width': '25%'})
        ]))
        display(HTML("</div>"))
        
        # Ligne 2 : Sources
        display(HTML("<div class='section-box'>"))
        display(HTML("<div class='section-title'>📁 Sources</div>"))
        display(HBox([
            VBox([HTML("<b>📎 Fichier</b>"), self.uploader, self.status_file], layout={'width': '30%'}),
            VBox([HTML("<b>📁 Drive</b>"), self.input_chemin], layout={'width': '30%'}),
            VBox([HTML("<b>✏️ Texte</b>"), self.input_texte], layout={'width': '40%'})
        ]))
        display(HTML("</div>"))
        
        # Ligne 3 : Type d'acte
        display(HTML("<div class='section-box'>"))
        display(HTML("<div class='section-title'>📜 Rédaction d'actes</div>"))
        display(HBox([self.type_acte_selector, self.btn_rediger_acte]))
        display(HTML("</div>"))
        
        # Ligne 4 : Actions
        display(HTML("<div class='section-box'>"))
        display(HTML("<div class='section-title'>📊 Actions</div>"))
        display(HBox([self.btn_analyser, self.btn_conclusions, self.btn_ameliorer, self.btn_email, self.btn_dalloz]))
        display(HBox([self.btn_tamponner, self.btn_sauvegarder, self.btn_sauvegarder_tout, self.btn_effacer]))
        display(HTML("</div>"))
        
        # Résultat
        display(HTML("<div class='section-box'>"))
        display(HTML("<div class='section-title'>📋 Résultat</div>"))
        display(self.output)
        display(HTML("</div>"))
        
        print("\n✅ Interface prête !")

# ========== UTILISATION ==========
# llm_client = LLM_Client(...)
# ui = AssistantUI(llm_client)
# ui.render()

# ============================================
# FONCTION DE COMPATIBILITÉ (interface existante)
# ============================================

def creer_interface(llm_client):
    """
    Fonction de compatibilité qui utilise la nouvelle classe AssistantUI
    """
    ui = AssistantUI(llm_client)
    ui.render()
    return ui