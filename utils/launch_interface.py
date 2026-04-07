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


def launch_interface(llm_client):
    """
    Lance l'interface à onglets complète avec toutes les fonctions connectées
    
    Args:
        llm_client: Client LLM configuré
        
    Returns:
        QuickTabbedUI: Instance de l'interface
    """
    # Créer l'interface
    ui = QuickTabbedUI(llm_client)
    
    # Connecter les fonctions
    ui.connect(
        analyser=lambda t: analyser_document(t, llm_client),
        conclusions=lambda t: preparer_conclusion(t, llm_client),
        ameliorer=lambda t: ameliorer_redaction(t, llm_client),
        email=lambda t: preparer_email(t, llm_client),
        dalloz=lambda t: rechercher_dalloz(t),
        rediger=lambda t, type_, instr: rediger_acte_juridique(t, llm_client, type_, instr),
        tampon=lambda t: appliquer_tampon(t, charger_config_tampon())
    )
    
    # Afficher
    ui.show()
    
    return ui


def create_interface(llm_client):
    """
    Alias de launch_interface
    """
    return launch_interface(llm_client)