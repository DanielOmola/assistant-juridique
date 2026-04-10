"""
launch_interface.py - Fonction de lancement rapide de l'interface
"""

from utils.utils_build_interface import QuickTabbedUI
from utils.utils_recherche_genial import rechercher_dalloz
from utils.utils_tampon import appliquer_tampon, charger_config_tampon
from utils.utils_action_rediger_acte import rediger_acte_juridique
from utils.utils_action_analyser_document import analyser_document
from utils.utils_action_preparer_conclusion import preparer_conclusion
from utils.utils_action_ameliorer_redaction import ameliorer_redaction
from utils.utils_action_preparer_email import preparer_email
from utils.utils_action_analyse_dossier import analyse_dossier
from utils.utils_action_prepare_audience import prepare_audience
from utils.utils_action_simuler_adversaire import simuler_adversaire
from utils.utils_action_generer_prompt import genere_prompt


def launch_interface(llm_client, templates):
    """
    Lance l'interface à onglets complète avec toutes les fonctions connectées
    
    Args:
        llm_client: Client LLM configuré
        
    Returns:
        QuickTabbedUI: Instance de l'interface
    """
    # Créer l'interface
    ui = QuickTabbedUI(llm_client, templates)
    
    # Connecter les fonctions avec les signatures correctes
    ui.connect(
        # Onglet Analyse & Action
        analyser=lambda t: analyser_document(t, llm_client),
        conclusions=lambda t: preparer_conclusion(t, llm_client),
        ameliorer=lambda t: ameliorer_redaction(t, llm_client),
        
        # Onglet Email client
        email=lambda t: preparer_email(t, llm_client),
        
        # Onglet Recherche
        recherche=lambda t: rechercher_dalloz(t),
        
        # Onglet Rédaction actes
        rediger=lambda t, type_, instr: rediger_acte_juridique(t, llm_client, type_, instr),
        
        # Onglet Tampon
        tampon=lambda t, config: appliquer_tampon(t, config),
        
        # Onglet Analyse dossier (multi-documents)
        analyse_dossier=lambda paths, client: analyse_dossier(paths, client),
        
        # Onglet Préparation audience
        preparer_audience=lambda analysis, client: prepare_audience(analysis, client),
        
        # Onglet Génération arguments
        generer_arguments=lambda analysis, client: simuler_adversaire(analysis, client),

        generer_prompt=lambda prompt_type, texte, template: (prompt_type, texte, template)
    )
    
    # Afficher l'interface
    ui.show()
    
    return ui


def create_interface(llm_client, templates):
    """
    Alias de launch_interface
    """
    return launch_interface(llm_client, templates)