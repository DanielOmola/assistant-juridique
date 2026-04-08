"""
tabbed_ui_complete.py - Interface à onglets complète pour Jupyter Notebook
"""
from utils.utils_logging import get_logger
from IPython.display import display, clear_output, Javascript
from ipywidgets import (
    Tab, VBox, HBox, Textarea, Button, Output, 
    FileUpload, Dropdown, HTML, Text, Checkbox,
    Label, IntSlider, FloatSlider
)
import os
from datetime import datetime
import re
import webbrowser

logger = get_logger(__name__)
_css_applied = False

class QuickTabbedUI:
    """
    Interface à onglets complète
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self._current_text = None
        self._current_filename = None
        self._last_result = None
        self._last_operation = None
        
        # Configuration
        self.save_path = "/content/drive/MyDrive/assistant-juridique"
        
        # Callbacks
        self.on_analyser = None
        self.on_conclusions = None
        self.on_ameliorer = None
        self.on_email = None
        self.on_recherche = None
        self.on_rediger = None
        self.on_tampon = None
        self.on_analyse_dossier = None
        self.on_preparer_audience = None
        self.on_generer_arguments = None
        
        # Références aux outputs pour mise à jour
        self.result_output = None
        self.analyse_output = None
        self.email_output = None
        self.redaction_output = None
        self.recherche_output = None
        self.tampon_output = None
        self.analyse_dossier_output = None
        self.stt_output = None
        self.ocr_output = None
        
        # Appliquer CSS
        global _css_applied
        if not _css_applied:
            display(HTML("""
            <style>
            .widget-tab > .p-TabBar .p-TabBar-tab { padding: 10px 20px; font-weight: 500; }
            .widget-tab > .p-TabBar .p-mod-current { color: #1a73e8; border-bottom: 2px solid #1a73e8; }
            button { border-radius: 8px !important; transition: 0.2s; }
            button:hover { transform: translateY(-1px); opacity: 0.9; }
            .result-box { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; max-height: 500px; overflow-y: auto; }
            .source-box { background: #f9fafc; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
            .link-button { background: #e8f0fe; color: #1a73e8; border: none; padding: 8px 12px; margin: 5px; border-radius: 20px; cursor: pointer; }
            .link-button:hover { background: #d2e3fc; }
            </style>
            """))
            _css_applied = True
        
        self._build_all_tabs()
    
    def _read_file_content(self, content, filename):
        """Lit le contenu d'un fichier uploadé"""
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
            return f"Erreur de lecture: {str(e)}"
    
    def _update_all_sources(self, text, filename):
        """Met à jour la source dans tous les onglets"""
        self._current_text = text
        self._current_filename = filename
        
        # Mettre à jour les statuts dans chaque onglet si les widgets existent
        if hasattr(self, '_source_statuses'):
            for status in self._source_statuses:
                if filename:
                    status.value = f"✅ {filename} validé ({len(text)} caractères)"
                else:
                    status.value = f"✅ Texte validé ({len(text)} caractères)"
    
    def _create_source_section(self, tab_name):
        """Crée une section source partagée entre tous les onglets"""
        
        source_text = Textarea(
            placeholder="Collez votre texte juridique ici...",
            layout={'width': '100%', 'height': '100px'}
        )
        
        source_file = FileUpload(
            accept='.txt,.pdf,.docx,.md',
            multiple=False,
            description='📂 Choisir un fichier',
            layout={'width': '100%'}
        )
        
        source_path = Textarea(
            placeholder="/content/drive/MyDrive/mon_document.pdf",
            layout={'width': '100%', 'height': '60px'}
        )
        
        source_status = HTML("📎 Aucune source")
        uploaded_content = None
        uploaded_filename = None
        
        btn_validate = Button(
            description="✅ Valider la source",
            button_style='primary',
            layout={'width': '200px'}
        )
        
        def on_upload_change(change):
            nonlocal uploaded_content, uploaded_filename
            if source_file.value:
                for filename, file_info in source_file.value.items():
                    uploaded_filename = filename
                    content = file_info['content']
                    uploaded_content = self._read_file_content(content, filename)
                    source_status.value = f"✅ {filename} chargé ({len(uploaded_content)} caractères)"
                
        def on_validate(b):
            nonlocal uploaded_content, uploaded_filename
            if source_text.value.strip():
                self._update_all_sources(source_text.value, None)
                source_status.value = f"✅ Texte validé ({len(source_text.value)} caractères)"
            elif source_path.value.strip():
                chemin = source_path.value.strip()
                if os.path.exists(chemin):
                    with open(chemin, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self._update_all_sources(content, os.path.basename(chemin))
                    source_status.value = f"✅ Fichier Drive validé: {os.path.basename(chemin)}"
                else:
                    source_status.value = "❌ Fichier introuvable"
            elif uploaded_content:
                self._update_all_sources(uploaded_content, uploaded_filename)
                source_status.value = f"✅ {uploaded_filename} validé ({len(uploaded_content)} caractères)"
            else:
                source_status.value = "❌ Aucune source sélectionnée"

        source_file.observe(on_upload_change, names='value')
        btn_validate.on_click(on_validate)
        
        # Stocker les références pour mise à jour globale
        if not hasattr(self, '_source_statuses'):
            self._source_statuses = []
        
        self._source_statuses.append(source_status)
        
        return VBox([
            HTML("<b>📄 Source du document</b>"),
            source_text,
            HTML("<br><b>📎 Upload fichier</b>"),
            source_file,
            HTML("<br><b>📁 Fichier Drive</b>"),
            source_path,
            HTML("<br>"),
            btn_validate,
            HTML("<br>"),
            source_status
        ])
    
    def _display_in_result_tab(self, content, operation):
        """Affiche le résultat dans l'onglet résultat"""
        self._last_result = content
        self._last_operation = operation
        
        # Afficher dans l'onglet résultat
        if self.result_output:
            with self.result_output:
                clear_output()
                display(HTML(f"""
                <div class='result-box'>
                    <div style='font-weight:bold; color:#1a73e8; margin-bottom:10px'>📊 {operation}</div>
                    <hr>
                    <div style='white-space:pre-wrap; font-family:monospace; font-size:12px'>{content}</div>
                </div>
                """))
        
        # Basculer vers l'onglet résultat
        for i in range(len(self.tabs.children)):
            if self.tabs.get_title(i) == "📋 Résultat":
                self.tabs.selected_index = i
                break
    
    def _build_config_tab(self):
        """Onglet Configuration"""
        
        api_status = HTML("")
        model_info = HTML("")
        
        model_options = []
        active_providers = []
        
        if self.llm:
            if hasattr(self.llm, 'API_KEYS'):
                for p in ['groq', 'openai', 'anthropic']:
                    if self.llm.API_KEYS.get(p):
                        active_providers.append(p)
            
            if hasattr(self.llm, 'MODELES_DISPONIBLES'):
                for model_id, info in self.llm.MODELES_DISPONIBLES.items():
                    provider = info.get('provider', '')
                    if provider in active_providers:
                        name = info.get('name', model_id)
                        model_options.append((f"{provider.upper()} - {name}", model_id))
            
            current_model = getattr(self.llm, 'modele_actif', None)
            if current_model and current_model in self.llm.MODELES_DISPONIBLES:
                current_name = self.llm.MODELES_DISPONIBLES[current_model].get('name', current_model)
                model_info.value = f"<span style='color:#1a73e8'>📌 Modèle actif: <b>{current_name}</b> ({current_model})</span>"
            else:
                model_info.value = "<span style='color:orange'>⚠️ Aucun modèle actif</span>"
        
        if not model_options:
            model_options = [("⚠️ Aucune clé API active", None)]
        
        self.model_selector = Dropdown(
            options=model_options,
            value=model_options[0][1] if model_options and model_options[0][1] else None,
            description="🤖 Choisir un modèle:",
            layout={'width': '100%'},
            style={'description_width': 'initial'}
        )
        
        self.temp_slider = FloatSlider(
            value=0.3,
            min=0.0,
            max=1.0,
            step=0.05,
            description="🌡️ Température (créativité):",
            layout={'width': '100%'}
        )
        
        self.max_tokens = IntSlider(
            value=4000,
            min=500,
            max=8000,
            step=500,
            description="📏 Max tokens (longueur réponse):",
            layout={'width': '100%'}
        )
        
        self.expert_mode = Checkbox(
            value=False,
            description="🔧 Mode expert (afficher plus de détails techniques)"
        )
        
        if active_providers:
            api_status.value = f"<span style='color:green'>✅ Clés API actives: {', '.join([p.upper() for p in active_providers])}</span>"
        else:
            api_status.value = "<span style='color:red'>❌ Aucune clé API active. Ajoutez vos clés dans les secrets.</span>"
        
        def on_model_change(change):
            if self.llm and change['new']:
                self.llm.modele_actif = change['new']
                if change['new'] in self.llm.MODELES_DISPONIBLES:
                    current_name = self.llm.MODELES_DISPONIBLES[change['new']].get('name', change['new'])
                    model_info.value = f"<span style='color:#1a73e8'>📌 Modèle actif: <b>{current_name}</b> ({change['new']})</span>"
        
        self.model_selector.observe(on_model_change, names='value')
        
        return VBox([
            HTML("<b>⚙️ Configuration</b>"),
            HTML("<hr>"),
            api_status,
            HTML("<br>"),
            model_info,
            HTML("<br>"),
            self.model_selector,
            HTML("<br>"),
            self.temp_slider,
            HTML("<br>"),
            self.max_tokens,
            HTML("<br>"),
            self.expert_mode,
            HTML("<br>"),
            HTML("<i>💡 Seuls les modèles correspondant à vos clés API sont affichés</i>")
        ], layout={'padding': '15px'})
    
    def _build_analyse_tab(self):
        """Onglet Analyse & Action"""
        
        self.analyse_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        def execute_analyser(b):
            if not self._current_text:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source. Validez d'abord une source.</span>"))
                return
            if not self.on_analyser:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction d'analyse non connectée</span>"))
                return
            
            with self.analyse_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🤖 Analyse en cours...</b></div>"))
            
            try:
                result = self.on_analyser(self._current_text)
                self._display_in_result_tab(result, "Analyse juridique")
            except Exception as e:
                with self.analyse_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        def execute_conclusions(b):
            if not self._current_text:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source</span>"))
                return
            if not self.on_conclusions:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction non connectée</span>"))
                return
            
            with self.analyse_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🤖 Rédaction des conclusions en cours...</b></div>"))
            
            try:
                result = self.on_conclusions(self._current_text)
                self._display_in_result_tab(result, "Conclusions juridiques")
            except Exception as e:
                with self.analyse_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        def execute_ameliorer(b):
            if not self._current_text:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source</span>"))
                return
            if not self.on_ameliorer:
                with self.analyse_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction non connectée</span>"))
                return
            
            with self.analyse_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🤖 Amélioration du texte en cours...</b></div>"))
            
            try:
                result = self.on_ameliorer(self._current_text)
                self._display_in_result_tab(result, "Texte amélioré")
            except Exception as e:
                with self.analyse_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_analyser = Button(description="🔍 Analyser", button_style='primary', layout={'width': '180px'})
        btn_conclusions = Button(description="⚖️ Conclusions", button_style='primary', layout={'width': '180px'})
        btn_ameliorer = Button(description="✨ Améliorer", button_style='primary', layout={'width': '180px'})
        
        btn_analyser.on_click(execute_analyser)
        btn_conclusions.on_click(execute_conclusions)
        btn_ameliorer.on_click(execute_ameliorer)
        
        return VBox([
            self._create_source_section("analyse"),
            HTML("<hr>"),
            HTML("<b>📊 Actions</b>"),
            HTML("<br>"),
            HBox([btn_analyser, btn_conclusions, btn_ameliorer], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.analyse_output
        ], layout={'padding': '15px'})


    def _build_analyse_dossier_tab(self):
        """Onglet Analyse de dossier complet (multi-documents)"""
        
        self.analyse_dossier_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        # Upload de multiples fichiers
        dossier_files = FileUpload(
            accept='.txt,.pdf,.docx,.md',
            multiple=True,
            description='📂 Choisir plusieurs fichiers',
            layout={'width': '100%'}
        )
        
        dossier_status = HTML("📎 Aucun fichier sélectionné")
        uploaded_texts = []
        
        def on_files_upload(change):
            nonlocal uploaded_texts
            if dossier_files.value:
                uploaded_texts = []
                for filename, file_info in dossier_files.value.items():
                    content = self._read_file_content(file_info['content'], filename)
                    uploaded_texts.append(content)
                dossier_status.value = f"✅ {len(uploaded_texts)} fichier(s) chargé(s)"
        
        def execute_analyse_dossier(b):
            if not uploaded_texts:
                with self.analyse_dossier_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun fichier sélectionné</span>"))
                return
            
            if not self.on_analyse_dossier:
                with self.analyse_dossier_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction d'analyse dossier non connectée</span>"))
                return
            
            with self.analyse_dossier_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>📁 Analyse du dossier en cours...</b></div>"))
            
            try:
                # Appeler la fonction connectée
                result = self.on_analyse_dossier(uploaded_texts, self.llm)
                self._display_in_result_tab(result, "Analyse complète du dossier")
            except Exception as e:
                with self.analyse_dossier_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_analyser = Button(description="📁 Analyser le dossier complet", button_style='primary', layout={'width': '250px'})
        btn_analyser.on_click(execute_analyse_dossier)
        dossier_files.observe(on_files_upload, names='value')
        
        return VBox([
            HTML("<b>📁 Analyse de dossier complet</b>"),
            HTML("<i>Sélectionnez tous les documents du dossier (PDF, DOCX, TXT)</i>"),
            HTML("<br><br>"),
            dossier_files,
            HTML("<br>"),
            dossier_status,
            HTML("<hr>"),
            HBox([btn_analyser], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.analyse_dossier_output
        ], layout={'padding': '15px'})    

    def _build_email_tab(self):
        """Onglet Email client"""
        
        self.email_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        def execute(b):
            if not self._current_text:
                with self.email_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source</span>"))
                return
            if not self.on_email:
                with self.email_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction email non connectée</span>"))
                return
            
            with self.email_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🤖 Rédaction de l'email en cours...</b></div>"))
            
            try:
                result = self.on_email(self._current_text)
                self._display_in_result_tab(result, "Email client")
            except Exception as e:
                with self.email_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_email = Button(description="📧 Générer l'email", button_style='primary', layout={'width': '250px'})
        btn_email.on_click(execute)
        
        return VBox([
            self._create_source_section("email"),
            HTML("<hr>"),
            HBox([btn_email], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.email_output
        ], layout={'padding': '15px'})
    
    def _build_redaction_tab(self):
        """Onglet Rédaction d'actes"""
        
        acte_type = Dropdown(
            options=[
                ("📄 Contrat", "contrat"),
                ("📝 Avenant", "avenant"),
                ("📜 Acte unilatéral", "acte_unilateral"),
                ("🤝 Convention", "convention"),
                ("✅ Quitus", "quitus"),
                ("⚖️ Assignation", "assignation"),
                ("📋 Mise en demeure", "mise_en_demeure")
            ],
            value="contrat",
            description="Type d'acte:",
            layout={'width': '100%'},
            style={'description_width': 'initial'}
        )
        
        instructions = Textarea(
            placeholder="Instructions spécifiques (clauses particulières, parties concernées, etc.)",
            layout={'width': '100%', 'height': '100px'}
        )
        
        self.redaction_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        def execute(b):
            if not self._current_text:
                with self.redaction_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source</span>"))
                return
            if not self.on_rediger:
                with self.redaction_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction de rédaction non connectée</span>"))
                return
            
            with self.redaction_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🤖 Rédaction de l'acte en cours...</b></div>"))
            
            try:
                result = self.on_rediger(self._current_text, acte_type.value, instructions.value)
                self._display_in_result_tab(result, f"Rédaction: {acte_type.value}")
            except Exception as e:
                with self.redaction_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_generer = Button(description="📜 Générer l'acte", button_style='primary', layout={'width': '250px'})
        btn_generer.on_click(execute)
        
        return VBox([
            self._create_source_section("redaction"),
            HTML("<hr>"),
            acte_type,
            instructions,
            HTML("<br>"),
            HBox([btn_generer], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.redaction_output
        ], layout={'padding': '15px'})
    
    def _build_recherche_tab(self):
        """Onglet Recherche avec liens externes"""
        
        recherche_input = Textarea(
            placeholder="Question ou thème juridique à rechercher...",
            layout={'width': '100%', 'height': '100px'}
        )
        
        self.recherche_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        # Fonction pour ouvrir les liens dans un nouvel onglet
        def open_link(url):
            def callback(b):
                display(Javascript(f'window.open("{url}", "_blank");'))
            return callback
        
        # Création des boutons de liens
        conseil_etat_btn = Button(description="🏛️ Conseil d'État", button_style='info', layout={'width': '160px'})
        courdecassation_btn = Button(description="🏛️ Cour de cassation", button_style='info', layout={'width': '160px'})
        dalloz_btn = Button(description="🔍 Dalloz", button_style='info', layout={'width': '130px'})
        doctrine_btn = Button(description="📚 Doctrine", button_style='info', layout={'width': '130px'})
        eur_lex_btn = Button(description="🇪🇺 EUR-Lex", button_style='info', layout={'width': '130px'})
        genial_btn = Button(description="🤖 GenIA-L", button_style='info', layout={'width': '130px'})
        justice_btn = Button(description="⚖️ Justice.fr", button_style='info', layout={'width': '130px'})
        legifrance_btn = Button(description="⚖️ Légifrance", button_style='info', layout={'width': '130px'})
        service_public_btn = Button(description="📖 Service Public", button_style='info', layout={'width': '150px'})
        
        # Attribution des callbacks
        dalloz_btn.on_click(open_link("https://www.dalloz.fr"))
        legifrance_btn.on_click(open_link("https://www.legifrance.gouv.fr"))
        doctrine_btn.on_click(open_link("https://www.doctrine.fr"))
        courdecassation_btn.on_click(open_link("https://www.courdecassation.fr"))
        conseil_etat_btn.on_click(open_link("https://www.conseil-etat.fr"))
        eur_lex_btn.on_click(open_link("https://eur-lex.europa.eu"))
        justice_btn.on_click(open_link("https://www.justice.fr"))
        genial_btn.on_click(open_link("https://genial-for-search.lefebvre-dalloz.fr/"))        
        service_public_btn.on_click(open_link("https://www.service-public.fr"))
        
        def execute(b):
            texte = recherche_input.value.strip() or self._current_text
            if not texte:
                with self.recherche_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Entrez une recherche ou validez d'abord une source.</span>"))
                return
            
            if not self.on_recherche:
                with self.recherche_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction de recherche non connectée</span>"))
                return
            
            with self.recherche_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🔍 Recherche en cours...</b></div>"))
            
            try:
                result = self.on_recherche(texte)
                self._display_in_result_tab(result, "Résultats de recherche")
            except Exception as e:
                with self.recherche_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_rechercher = Button(description="🔍 Lancer la recherche", button_style='primary', layout={'width': '250px'})
        btn_rechercher.on_click(execute)
        
        return VBox([
            HTML("<b>🔍 Recherche juridique</b>"),
            HTML("<br>"),
            recherche_input,
            HTML("<br><i>💡 Laissez vide pour utiliser le texte source validé</i>"),
            HTML("<br><br>"),
            HTML("<b>📚 Sources juridiques externes:</b>"),
            HTML("<br>"),
            HBox([genial_btn, dalloz_btn, legifrance_btn, doctrine_btn], layout={'flex_wrap': 'wrap'}),
            HBox([courdecassation_btn, conseil_etat_btn, eur_lex_btn], layout={'flex_wrap': 'wrap'}),
            HBox([justice_btn, service_public_btn], layout={'flex_wrap': 'wrap'}),
            HTML("<br><hr><br>"),
            HBox([btn_rechercher], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.recherche_output
        ], layout={'padding': '15px'})
    
    def _build_tampon_tab(self):
        """Onglet Tampon avec partage des fichiers"""
        
        source_file = FileUpload(
            accept='.txt,.pdf,.docx,.md',
            multiple=False,
            description='📂 Choisir un fichier à tamponner',
            layout={'width': '100%'}
        )
        
        source_path = Textarea(
            placeholder="/content/drive/MyDrive/mon_document.pdf",
            layout={'width': '100%', 'height': '60px'}
        )
        
        source_status = HTML("📎 Aucun fichier")
        uploaded_content = None
        uploaded_filename = None
        
        # Champs avocat
        nom = Text(description="Nom:", layout={'width': '200px'})
        prenom = Text(description="Prénom:", layout={'width': '200px'})
        fonction = Text(description="Fonction:", layout={'width': '200px'})
        barreau = Text(description="Barreau:", layout={'width': '200px'})
        email = Text(description="Email:", layout={'width': '250px'})
        
        tampon_type = Dropdown(
            options=[("Officiel", "officiel"), ("Confidentiel", "confidentiel"), 
                     ("Reçu", "recu"), ("Brouillon", "brouillon"), ("Copie conforme", "copie_conforme")],
            description="Type:",
            layout={'width': '200px'}
        )
        
        position = Dropdown(
            options=[("Début", "debut"), ("Fin", "fin"), ("Début + Fin", "debut_et_fin")],
            description="Position:",
            layout={'width': '200px'}
        )
        
        apercu = HTML("<pre style='background:#f5f5f5; padding:10px; border-radius:8px'></pre>")
        
        self.tampon_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        def on_upload_change(change):
            nonlocal uploaded_content, uploaded_filename
            if source_file.value:
                for filename, file_info in source_file.value.items():
                    uploaded_filename = filename
                    content = file_info['content']
                    uploaded_content = self._read_file_content(content, filename)
                    source_status.value = f"✅ {filename} chargé"
                    source_path.value = ""
        
        def update_preview(*args):
            preview = f"""
[{tampon_type.value.upper()}]
{nom.value} {prenom.value}
{fonction.value}
Avocat au Barreau de {barreau.value}
{email.value}
"""
            apercu.value = f"<pre style='background:#f5f5f5; padding:10px; border-radius:8px'>{preview}</pre>"
        
        def validate_file(b):
            nonlocal uploaded_content, uploaded_filename
            if source_path.value.strip():
                chemin = source_path.value.strip()
                if os.path.exists(chemin):
                    with open(chemin, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self._update_all_sources(content, os.path.basename(chemin))
                    source_status.value = f"✅ Fichier Drive validé: {os.path.basename(chemin)}"
                else:
                    source_status.value = "❌ Fichier introuvable"
            elif uploaded_content:
                self._update_all_sources(uploaded_content, uploaded_filename)
                source_status.value = f"✅ {uploaded_filename} validé"
            else:
                source_status.value = "❌ Aucun fichier sélectionné"

        source_file.observe(on_upload_change, names='value')
        for w in [nom, prenom, fonction, barreau, email, tampon_type]:
            w.observe(update_preview, names='value')
        
        update_preview()
        
        btn_valider_fichier = Button(description="✅ Valider le fichier", button_style='primary', layout={'width': '200px'})
        btn_valider_fichier.on_click(validate_file)
        
        def execute(b):
            if not self._current_text:
                with self.tampon_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun fichier. Validez d'abord un fichier.</span>"))
                return
            
            if not self.on_tampon:
                with self.tampon_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction de tampon non connectée</span>"))
                return
            
            config = {
                'avocat': {
                    'nom': nom.value,
                    'prenom': prenom.value,
                    'fonction': fonction.value,
                    'barreau': barreau.value,
                    'email': email.value
                },
                'options': {
                    'type_tampon': tampon_type.value,
                    'position': position.value
                }
            }
            
            with self.tampon_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🖊️ Application du tampon en cours...</b></div>"))
            
            try:
                result = self.on_tampon(self._current_text, config)
                self._display_in_result_tab(result, "Document tamponné")
            except Exception as e:
                with self.tampon_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_appliquer = Button(description="🖊️ Appliquer le tampon", button_style='warning', layout={'width': '250px'})
        btn_appliquer.on_click(execute)
        
        return VBox([
            HTML("<b>🖊️ Tamponner un document</b>"),
            HTML("<hr>"),
            HTML("<b>📁 Sélectionner un fichier</b>"),
            source_file,
            source_path,
            HTML("<br>"),
            HBox([btn_valider_fichier]),
            source_status,
            HTML("<hr>"),
            HTML("<b>⚙️ Configuration du tampon</b>"),
            HBox([nom, prenom, fonction]),
            HBox([barreau, email]),
            HBox([tampon_type, position]),
            HTML("<br><b>📋 Aperçu</b>"),
            apercu,
            HTML("<br>"),
            HBox([btn_appliquer], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.tampon_output
        ], layout={'padding': '15px'})
    
    def _build_preparer_audience_tab(self):
        """Onglet Préparation d'audience"""
        
        self.audience_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        type_audience = Dropdown(
            options=[
                ("Audience civile", "civile"),
                ("Audience pénale", "penale"),
                ("Audience administrative", "administrative")
            ],
            description="Type d'audience:",
            layout={'width': '100%'}
        )
        
        objectif = Textarea(
            placeholder="Objectif (ex: obtenir nullité, réduire condamnation, obtenir gain de cause...)",
            layout={'width': '100%', 'height': '80px'}
        )
        
        def execute(b):
            if not self._current_text:
                with self.audience_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucune analyse de dossier. Validez d'abord une source ou analysez un dossier.</span>"))
                return
            
            if not self.on_preparer_audience:
                with self.audience_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction de préparation audience non connectée</span>"))
                return
            
            with self.audience_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>⚖️ Préparation de l'audience en cours...</b></div>"))
            
            try:
                # Signature correcte: prepare_audience(case_analysis, llm_client)
                result = self.on_preparer_audience(self._current_text, self.llm)
                self._display_in_result_tab(result, "Préparation d'audience")
            except Exception as e:
                with self.audience_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_preparer = Button(description="⚖️ Préparer l'audience", button_style='primary', layout={'width': '250px'})
        btn_preparer.on_click(execute)
        
        return VBox([
            self._create_source_section("audience"),
            HTML("<hr>"),
            type_audience,
            objectif,
            HTML("<br>"),
            HBox([btn_preparer], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.audience_output
        ], layout={'padding': '15px'})
    
    def _build_generer_arguments_tab(self):
        """Onglet Génération d'arguments juridiques"""
        
        self.arguments_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        strategie = Dropdown(
            options=[
                ("Défense", "defense"),
                ("Attaque", "attaque"),
                ("Neutre / analyse", "neutre")
            ],
            description="Stratégie:",
            layout={'width': '100%'}
        )
        
        def execute(b):
            if not self._current_text:
                with self.arguments_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun texte source</span>"))
                return
            
            if not self.on_generer_arguments:
                with self.arguments_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Fonction de génération d'arguments non connectée</span>"))
                return
            
            with self.arguments_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🧠 Génération des arguments en cours...</b></div>"))
            
            try:
                result = self.on_generer_arguments(self._current_text, self.llm)
                self._display_in_result_tab(result, f"Arguments juridiques - {strategie.value}")
            except Exception as e:
                with self.arguments_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_generer = Button(description="🧠 Générer les arguments", button_style='primary', layout={'width': '250px'})
        btn_generer.on_click(execute)
        
        return VBox([
            self._create_source_section("arguments"),
            HTML("<hr>"),
            strategie,
            HTML("<br>"),
            HBox([btn_generer], layout={'justify_content': 'center'}),
            HTML("<hr>"),
            self.arguments_output
        ], layout={'padding': '15px'})
    
    def _build_save_section(self):
        """Section sauvegarde pour l'onglet résultat"""
        
        save_path_input = Text(
            value=self.save_path,
            description="Dossier de sauvegarde:",
            layout={'width': '100%'},
            style={'description_width': 'initial'}
        )
        
        save_filename = Text(
            description="Nom du fichier:",
            placeholder="auto (laissé vide)",
            layout={'width': '100%'},
            style={'description_width': 'initial'}
        )
        
        btn_save = Button(
            description="💾 Sauvegarder le résultat",
            button_style='success',
            layout={'width': '200px'}
        )
        
        btn_copy = Button(
            description="📋 Copier le résultat",
            button_style='info',
            layout={'width': '200px'}
        )
        
        save_status = HTML("")
        
        def on_save(b):
            if not self._last_result:
                save_status.value = "<span style='color:orange'>⚠️ Aucun résultat à sauvegarder</span>"
                return
            
            dossier = save_path_input.value
            if dossier and not os.path.exists(dossier):
                os.makedirs(dossier, exist_ok=True)
            
            if save_filename.value.strip():
                nom_fichier = save_filename.value.strip()
                if not nom_fichier.endswith('.txt'):
                    nom_fichier += '.txt'
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base = self._current_filename or "document"
                base = re.sub(r'[<>:"/\\|?*]', '_', base)
                operation = self._last_operation or "resultat"
                operation = re.sub(r'[<>:"/\\|?*]', '_', operation)
                nom_fichier = f"{base}_{operation}_{timestamp}.txt"
            
            chemin_complet = os.path.join(dossier, nom_fichier) if dossier else nom_fichier
            
            try:
                with open(chemin_complet, 'w', encoding='utf-8') as f:
                    f.write(self._last_result)
                save_status.value = f"<span style='color:green'>✅ Sauvegardé: {chemin_complet}</span>"
            except Exception as e:
                save_status.value = f"<span style='color:red'>❌ Erreur: {str(e)}</span>"
        
        def on_copy(b):
            if self._last_result:
                text_to_copy = self._last_result.replace('`', '\\`').replace('${', '\\${')
                display(Javascript(f"""
                    navigator.clipboard.writeText(`{text_to_copy}`);
                """))
                save_status.value = "<span style='color:green'>✅ Copié dans le presse-papier</span>"
            else:
                save_status.value = "<span style='color:orange'>⚠️ Aucun résultat à copier</span>"
        
        btn_save.on_click(on_save)
        btn_copy.on_click(on_copy)
        
        return VBox([
            HTML("<b>💾 Sauvegarde</b>"),
            save_path_input,
            save_filename,
            HTML("<br>"),
            HBox([btn_save, btn_copy]),
            save_status
        ])
    
    def _build_result_tab(self):
        """Onglet Résultat avec sauvegarde et copie"""
        
        self.result_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        return VBox([
            HTML("<b>📊 Résultat</b>"),
            HTML("<hr>"),
            self.result_output,
            HTML("<hr>"),
            self._build_save_section()
        ], layout={'padding': '15px'})
    
    def _build_stt_tab(self):
        """Onglet Dictée vocale"""
        
        self.stt_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        
        instructions = HTML("""
        <div style='background:#e8f0fe; padding:15px; border-radius:10px; margin:10px 0'>
            <b>🎤 Dictée vocale - Méthode simple :</b><br><br>
            <b>Option 1 : Téléphone (recommandé)</b><br>
            1. Enregistrez-vous avec l'appli "Dictaphone" de votre téléphone<br>
            2. Envoyez-vous le fichier par email / WhatsApp / Drive<br>
            3. Téléchargez-le ci-dessous<br>
            4. Cliquez sur "Transcrire"<br><br>
            <b>Option 2 : En direct sur l'ordinateur</b><br>
            1. Utilisez l'outil "Dictée" intégré de Windows/Mac (Win+H ou Cmd+Shift+D)<br>
            2. Dictez votre texte directement dans la zone ci-dessous<br>
            3. Puis cliquez sur "Analyser"<br><br>
            <b>💡 Astuce :</b> La transcription est plus précise avec un fichier audio de bonne qualité.
        </div>
        """)
        
        audio_uploader = FileUpload(
            accept='.wav,.mp3,.m4a,.mpeg',
            multiple=False,
            description='📂 Choisir un fichier audio',
            layout={'width': '100%'}
        )
        
        btn_transcribe = Button(description="📝 Transcrire l'audio", 
                                button_style='primary',
                                layout={'width': '250px'})
        
        transcription_text = Textarea(
            placeholder="La transcription apparaîtra ici...",
            layout={'width': '100%', 'height': '150px'}
        )
        
        def on_transcribe(b):
            if not audio_uploader.value:
                with self.stt_output:
                    clear_output()
                    display(HTML("<span style='color:red'>❌ Aucun fichier audio</span>"))
                return
            
            with self.stt_output:
                clear_output()
                display(HTML("<div style='text-align:center;padding:20px'><b>📝 Transcription en cours...</b></div>"))
            
            try:
                for filename, file_info in audio_uploader.value.items():
                    content = file_info['content']
                    temp_path = f"/tmp/{filename}"
                    with open(temp_path, 'wb') as f:
                        f.write(content)
                    
                    if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'audio'):
                        with open(temp_path, 'rb') as f:
                            response = self.llm.client.audio.transcriptions.create(
                                model="whisper-large-v3",
                                file=f,
                                language="fr"
                            )
                        transcription = response.text
                        transcription_text.value = transcription
                        self._current_text = transcription
                        
                        with self.stt_output:
                            clear_output()
                            display(HTML(f"""
                            <div class='result-box'>
                                <div style='font-weight:bold;color:#1a73e8'>✅ Transcription</div>
                                <hr>
                                <div style='white-space:pre-wrap'>{transcription}</div>
                            </div>
                            """))
                    else:
                        with self.stt_output:
                            clear_output()
                            display(HTML("<span style='color:orange'>⚠️ API de transcription non configurée</span>"))
                            
            except Exception as e:
                with self.stt_output:
                    clear_output()
                    display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
        
        btn_transcribe.on_click(on_transcribe)
        
        return VBox([
            HTML("<b>🎤 Dictée vocale</b>"),
            instructions,
            HTML("<br><b>📁 Upload audio :</b>"),
            audio_uploader,
            HTML("<br>"),
            HBox([btn_transcribe], layout={'justify_content': 'center'}),
            HTML("<br>"),
            self.stt_output,
            HTML("<br><b>📝 Transcription :</b>"),
            transcription_text
        ])
    
    def _build_ocr_tab(self):
        """Onglet Scan de documents (PDF scannés)"""
        
        self.ocr_output = Output(layout={'width': '100%', 'max_height': '500px', 'overflow_y': 'auto'})
        self.ocr_status = HTML("📄 Aucun document")
        
        self.ocr_uploader = FileUpload(
            accept='.pdf,.jpg,.png,.jpeg',
            multiple=False,
            description='📂 Choisir un PDF scanné ou une photo',
            layout={'width': '100%'}
        )
        
        btn_extract = Button(description="🔍 Extraire le texte", 
                            button_style='primary',
                            layout={'width': '250px'})
        
        self.ocr_text = Textarea(
            placeholder="Le texte extrait apparaîtra ici...",
            layout={'width': '100%', 'height': '200px'}
        )
        
        self.ocr_content = None
        self.ocr_filename = None
        
        def on_upload_change(change):
            if self.ocr_uploader.value:
                for filename, file_info in self.ocr_uploader.value.items():
                    self.ocr_filename = filename
                    content = file_info['content']
                    temp_path = f"/tmp/{filename}"
                    with open(temp_path, 'wb') as f:
                        f.write(content)
                    self.ocr_content = temp_path
                    self.ocr_status.value = f"✅ {filename} chargé ({len(content)} octets)"
        
        def on_extract(b):
            if not self.ocr_content:
                self.ocr_status.value = "❌ Aucun document"
                return
            
            with self.ocr_output:
                clear_output()
                display(HTML("<div style='text-align:center; padding:20px'><b>🔍 Extraction en cours...</b></div>"))
            
            try:
                if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'chat'):
                    import base64
                    with open(self.ocr_content, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode()
                    
                    response = self.llm.client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extrais tout le texte de ce document juridique."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                            ]
                        }]
                    )
                    texte_extrait = response.choices[0].message.content
                else:
                    texte_extrait = """
⚠️ Pour extraire le texte d'un PDF scanné :

1. Ouvrez ce PDF dans Google Drive
2. Faites clic droit → "Ouvrir avec Google Docs"
3. Copiez le texte généré
4. Collez-le ci-dessus

Ou utilisez un outil en ligne gratuit : https://www.ilovepdf.com/fr/pdf_en_texte
"""
                
                self.ocr_text.value = texte_extrait
                self._current_text = texte_extrait
                self.ocr_status.value = "✅ Texte extrait avec succès"
                
                with self.ocr_output:
                    clear_output()
                    display(HTML(f"""
                    <div class='result-box'>
                        <div style='font-weight:bold; color:#1a73e8'>📄 Texte extrait</div>
                        <hr>
                        <div style='white-space:pre-wrap; max-height:400px; overflow-y:auto'>{texte_extrait[:3000]}</div>
                    </div>
                    """))
                    
            except Exception as e:
                self.ocr_status.value = f"❌ Erreur: {str(e)}"
        
        self.ocr_uploader.observe(on_upload_change, names='value')
        btn_extract.on_click(on_extract)
        
        return VBox([
            HTML("<b>📄 Scanner un document</b>"),
            HTML("<i>Importez un PDF scanné ou une photo de document</i>"),
            HTML("<br>"),
            self.ocr_uploader,
            HTML("<br>"),
            HBox([btn_extract], layout={'justify_content': 'center'}),
            HTML("<br>"),
            self.ocr_status,
            HTML("<br>"),
            HTML("<b>📝 Texte extrait :</b>"),
            self.ocr_text
        ])
    
    def _build_all_tabs(self):
        """Construit tous les onglets"""
        
        self.tabs = Tab([
            self._build_config_tab(),           # 0: Configuration
            self._build_analyse_tab(),          # 1: Analyse & Action
            self._build_analyse_dossier_tab(),  # 2: Analyse dossier complet
            self._build_preparer_audience_tab(),# 3: Préparation audience
            self._build_generer_arguments_tab(),# 4: Génération arguments
            self._build_email_tab(),            # 5: Email client
            self._build_redaction_tab(),        # 6: Rédaction actes
            self._build_recherche_tab(),        # 7: Recherche
            self._build_tampon_tab(),           # 8: Tampon
            self._build_stt_tab(),              # 9: Dictée vocale
            self._build_ocr_tab(),              # 10: Scan documents
            self._build_result_tab()            # 11: Résultat
        ])
        
        self.tabs.set_title(0, "⚙️ Configuration")
        self.tabs.set_title(1, "📊 Analyse & Action")
        self.tabs.set_title(2, "📁 Analyse dossier")
        self.tabs.set_title(3, "⚖️ Préparer audience")
        self.tabs.set_title(4, "🧠 Arguments")
        self.tabs.set_title(5, "📧 Email client")
        self.tabs.set_title(6, "📜 Rédiger actes")
        self.tabs.set_title(7, "🔍 Recherche")
        self.tabs.set_title(8, "🖊️ Tampon")
        self.tabs.set_title(9, "🎤 Dictée")
        self.tabs.set_title(10, "📄 Scan")
        self.tabs.set_title(11, "📋 Résultat")
    
    def connect(self, analyser=None, conclusions=None, ameliorer=None,
                email=None, recherche=None, dalloz=None, rediger=None, 
                tampon=None, analyse_dossier=None, preparer_audience=None,
                generer_arguments=None):
        """
        Connecte les fonctions de traitement
        """
        self.on_analyser = analyser
        self.on_conclusions = conclusions
        self.on_ameliorer = ameliorer
        self.on_email = email
        self.on_recherche = recherche or dalloz
        self.on_rediger = rediger
        self.on_tampon = tampon
        self.on_analyse_dossier = analyse_dossier
        self.on_preparer_audience = preparer_audience
        self.on_generer_arguments = generer_arguments
    
    def show(self):
        """Affiche l'interface"""
        display(HTML("<h1 style='color:#1a73e8; text-align:center; margin-bottom:20px'>⚖️ Juribot - Interface complète</h1>"))
        display(self.tabs)
    
    def get_current_text(self):
        return self._current_text
    
    def get_last_result(self):
        return self._last_result