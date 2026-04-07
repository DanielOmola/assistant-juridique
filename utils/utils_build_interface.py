"""
tabbed_ui_light.py - Interface à onglets ultra-légère (version corrigée)
"""

from IPython.display import display, clear_output
from ipywidgets import (
    Tab, VBox, HBox, Textarea, Button, Output, 
    FileUpload, Dropdown, HTML
)
import os
from datetime import datetime

# CSS à appliquer une seule fois
_css_applied = False

class QuickTabbedUI:
    """
    Interface à onglets - utilisation en 3 lignes:
    
        ui = QuickTabbedUI(llm_client)
        ui.connect(analyser, conclusions, ameliorer, email, dalloz, rediger_acte, tamponner)
        ui.show()
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self._callbacks = {}
        self._current_text = None
        
        # Appliquer CSS une seule fois
        global _css_applied
        if not _css_applied:
            display(HTML("""
            <style>
            .widget-tab > .p-TabBar .p-TabBar-tab { padding: 10px 20px; font-weight: 500; }
            .widget-tab > .p-TabBar .p-mod-current { color: #1a73e8; border-bottom: 2px solid #1a73e8; }
            button { border-radius: 8px !important; transition: 0.2s; }
            button:hover { transform: translateY(-1px); }
            </style>
            """))
            _css_applied = True
        
        self._build()
    
    def _build(self):
        # Source
        self.source_text = Textarea(
            placeholder="Collez votre texte juridique ici...",
            layout={'width': '100%', 'height': '120px'}
        )
        
        self.source_file = FileUpload(
            accept='.txt,.pdf,.docx',
            multiple=False,
            description='📂 Choisir un fichier'
        )
        
        self.source_status = HTML("📎 Aucune source")
        
        self.btn_validate = Button(
            description="✅ Valider la source",
            button_style='primary',
            layout={'width': '200px'}
        )
        
        def validate(b):
            if self.source_text.value.strip():
                self._current_text = self.source_text.value
                self.source_status.value = "✅ Texte validé"
            elif self.source_file.value:
                for name, info in self.source_file.value.items():
                    content = info['content']
                    try:
                        self._current_text = content.decode('utf-8')
                        self.source_status.value = f"✅ {name} chargé"
                    except:
                        self.source_status.value = f"❌ Erreur lecture {name}"
            else:
                self.source_status.value = "❌ Aucune source sélectionnée"
        
        self.btn_validate.on_click(validate)
        
        # Boutons actions
        self.btn_analyser = Button(
            description="🔍 Analyser",
            button_style='primary',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_conclusions = Button(
            description="⚖️ Conclusions",
            button_style='primary',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_ameliorer = Button(
            description="✨ Améliorer",
            button_style='primary',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_email = Button(
            description="📧 Email client",
            button_style='info',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_dalloz = Button(
            description="🔍 Recherche Dalloz",
            button_style='info',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_rediger = Button(
            description="📜 Rédiger acte",
            button_style='primary',
            layout={'width': '150px', 'margin': '5px'}
        )
        self.btn_tampon = Button(
            description="🖊️ Appliquer tampon",
            button_style='warning',
            layout={'width': '150px', 'margin': '5px'}
        )
        
        # Type d'acte
        self.acte_type = Dropdown(
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
        
        # Résultat
        self.output = Output(
            layout={'width': '100%', 'height': '400px', 'overflow_y': 'auto'}
        )
        
        # Assemblage des onglets
        source_tab = VBox([
            self.source_text,
            self.source_file,
            self.btn_validate,
            self.source_status
        ], layout={'padding': '15px'})
        
        actions_tab = VBox([
            HBox([self.btn_analyser, self.btn_conclusions, self.btn_ameliorer]),
            HBox([self.btn_email, self.btn_dalloz]),
            HBox([self.acte_type, self.btn_rediger]),
            self.btn_tampon
        ], layout={'padding': '15px'})
        
        result_tab = VBox([self.output], layout={'padding': '15px'})
        
        self.tabs = Tab([source_tab, actions_tab, result_tab])
        self.tabs.set_title(0, "📄 Source")
        self.tabs.set_title(1, "🔧 Actions")
        self.tabs.set_title(2, "📊 Résultat")
    
    def connect(self, analyser=None, conclusions=None, ameliorer=None, 
                email=None, dalloz=None, rediger=None, tampon=None):
        """
        Connecte vos fonctions existantes en une ligne
        
        Args:
            analyser: fonction(texte) -> str
            conclusions: fonction(texte) -> str
            ameliorer: fonction(texte) -> str
            email: fonction(texte) -> str
            dalloz: fonction(texte) -> str
            rediger: fonction(texte, type_acte) -> str
            tampon: fonction(texte) -> str
        """
        self._callbacks = {
            'analyser': analyser, 'conclusions': conclusions, 'ameliorer': ameliorer,
            'email': email, 'dalloz': dalloz, 'rediger': rediger, 'tampon': tampon
        }
        
        if analyser:
            self.btn_analyser.on_click(lambda b: self._run(analyser, "📄 Analyse"))
        if conclusions:
            self.btn_conclusions.on_click(lambda b: self._run(conclusions, "⚖️ Conclusions"))
        if ameliorer:
            self.btn_ameliorer.on_click(lambda b: self._run(ameliorer, "✨ Amélioration"))
        if email:
            self.btn_email.on_click(lambda b: self._run(email, "📧 Email client"))
        if dalloz:
            self.btn_dalloz.on_click(lambda b: self._run(dalloz, "🔍 Recherche Dalloz"))
        if rediger:
            self.btn_rediger.on_click(lambda b: self._run(
                lambda t: rediger(t, self.acte_type.value), 
                f"📜 Rédaction {self.acte_type.value}"
            ))
        if tampon:
            self.btn_tampon.on_click(lambda b: self._run(tampon, "🖊️ Application du tampon"))
    
    def _run(self, func, title):
        """Exécute une fonction et affiche le résultat"""
        if not self._current_text:
            with self.output:
                clear_output()
                display(HTML("<span style='color:red'>❌ Aucun texte source. Validez d'abord une source dans l'onglet Source.</span>"))
            self.tabs.selected_index = 0
            return
        
        with self.output:
            clear_output()
            display(HTML(f"<div style='text-align:center; padding:20px'><b>🤖 {title} en cours...</b><br><i>Cela peut prendre quelques secondes</i></div>"))
        
        try:
            result = func(self._current_text)
            with self.output:
                clear_output()
                display(HTML(f"""
                <div style='background:white; padding:15px; border-radius:10px; border:1px solid #e0e0e0'>
                    <div style='font-weight:bold; color:#1a73e8; margin-bottom:10px'>📊 {title}</div>
                    <hr style='margin:10px 0'>
                    <div style='white-space:pre-wrap; font-family:monospace; font-size:12px'>{result}</div>
                </div>
                """))
            self.tabs.selected_index = 2
        except Exception as e:
            with self.output:
                clear_output()
                display(HTML(f"<span style='color:red'>❌ Erreur: {str(e)}</span>"))
    
    def show(self):
        """Affiche l'interface"""
        display(HTML("<h2 style='color:#1a73e8; text-align:center; margin-bottom:10px'>⚖️ Juribot</h2>"))
        display(self.tabs)
    
    def get_current_text(self):
        """Retourne le texte source actuel"""
        return self._current_text
    
    def set_text(self, texte):
        """Définit le texte source programmatiquement"""
        self._current_text = texte
        self.source_text.value = texte
        self.source_status.value = "✅ Texte chargé"