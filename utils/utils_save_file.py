# ============================================
# 7. FONCTIONS DE SAUVEGARDE INTELLIGENTE
# ============================================
import os
import re
from datetime import datetime
from google.colab import files
from ipywidgets import Text, Checkbox, VBox, HBox, Button as WButton
from IPython.display import display, clear_output, Markdown
from ipywidgets import (
    Textarea, Button, Output, VBox, HBox, HTML,
    FileUpload, Dropdown, Label
)
from utils.utils_logging import get_logger

logger = get_logger(__name__)

# Dossier par défaut pour les fichiers externes
DOSSIER_BASE_EXTERNE = "/content/drive/MyDrive/assistant-juridique"

def sanitize_filename(nom: str) -> str:
    """Nettoie un nom de fichier (enlève caractères interdits)"""
    nom_propre = re.sub(r'[<>:"/\\|?*]', '_', nom)
    logger.debug(f"Sanitize filename: '{nom}' → '{nom_propre}'")
    return nom_propre

def generer_nom_fichier(original: str, suffixe: str, extension: str = "txt") -> str:
    """Génère un nom de fichier par défaut basé sur l'original"""
    base = os.path.splitext(os.path.basename(original))[0]
    base = sanitize_filename(base)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"{base}_{suffixe}_{timestamp}.{extension}"
    logger.debug(f"Nom fichier généré: {nom_fichier} (original: {original}, suffixe: {suffixe})")
    return nom_fichier

def get_dossier_origine(chemin_fichier: str) -> str:
    """Retourne le dossier d'origine d'un fichier Drive"""
    if chemin_fichier and chemin_fichier.startswith('/content/drive/'):
        dossier = os.path.dirname(chemin_fichier)
        logger.debug(f"Dossier d'origine Drive: {dossier}")
        return dossier
    logger.debug(f"Aucun dossier Drive trouvé pour: {chemin_fichier}")
    return None

def sauvegarder_texte(contenu: str, chemin_complet: str) -> bool:
    """Sauvegarde du texte dans un fichier"""
    try:
        # Log du début
        logger.info(f"💾 Sauvegarde demandée - {len(contenu)} caractères vers {chemin_complet}")
        
        # Créer le dossier si nécessaire
        dossier = os.path.dirname(chemin_complet)
        if dossier and not os.path.exists(dossier):
            os.makedirs(dossier)
            logger.debug(f"Dossier créé: {dossier}")

        with open(chemin_complet, 'w', encoding='utf-8') as f:
            f.write(contenu)

        logger.info(f"✅ Sauvegarde réussie - {os.path.basename(chemin_complet)} ({len(contenu)} caractères)")
        print(f"✅ Fichier sauvegardé : {chemin_complet}")
        return True
        
    except PermissionError as e:
        logger.error(f"❌ Permission refusée pour {chemin_complet}: {str(e)}")
        print(f"❌ Erreur permission : {str(e)}")
        return False
        
    except OSError as e:
        logger.error(f"❌ Erreur système lors de la sauvegarde: {str(e)}")
        print(f"❌ Erreur système : {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue sauvegarde: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        print(f"❌ Erreur sauvegarde : {str(e)}")
        return False

def afficher_dialogue_sauvegarde(contenu: str, fichier_original: str, type_generation: str):
    """
    Affiche une boîte de dialogue pour configurer la sauvegarde
    fichier_original: chemin du fichier source ou None
    type_generation: "analyse", "conclusions", "amelioration", "email"
    """
    
    logger.info(f"📋 Dialogue sauvegarde ouvert - Type: {type_generation}, Fichier original: {fichier_original is not None}")
    logger.debug(f"Contenu à sauvegarder: {len(contenu)} caractères")

    # Déterminer le suffixe selon le type
    suffixes = {
        "analyse": "analyse",
        "conclusions": "conclusions",
        "amelioration": "amelioration",
        "email": "email"
    }
    suffixe = suffixes.get(type_generation, "generation")

    # Déterminer le dossier et nom par défaut
    dossier_origine = None
    nom_original = "document"
    type_source = "texte"

    if fichier_original and fichier_original.startswith('/content/drive/'):
        # Fichier Drive : sauvegarde au même endroit
        dossier_origine = os.path.dirname(fichier_original)
        nom_original = os.path.basename(fichier_original)
        chemin_defaut = os.path.join(dossier_origine, generer_nom_fichier(nom_original, suffixe))
        type_source = "drive"
        logger.info(f"📁 Sauvegarde dans Drive - Dossier: {dossier_origine}")
        
    elif fichier_original:
        # Fichier externe : créer un dossier dédié
        nom_original = os.path.basename(fichier_original)
        dossier_dedie = os.path.join(DOSSIER_BASE_EXTERNE, sanitize_filename(nom_original.replace('.', '_')))
        chemin_defaut = os.path.join(dossier_dedie, generer_nom_fichier(nom_original, suffixe))
        type_source = "externe"
        logger.info(f"📁 Sauvegarde fichier externe - Dossier dédié: {dossier_dedie}")
        
    else:
        # Pas de fichier source (texte collé)
        chemin_defaut = os.path.join(DOSSIER_BASE_EXTERNE, f"generation_{suffixe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        type_source = "texte"
        logger.info(f"📝 Sauvegarde texte saisi - Dossier: {DOSSIER_BASE_EXTERNE}")

    logger.debug(f"Chemin par défaut: {chemin_defaut}")

    # Widgets
    label_info = HTML(f"<b>💾 Sauvegarder le {type_generation}</b>")

    chemin_input = Text(
        value=chemin_defaut,
        description="📁 Chemin:",
        layout={'width': '90%'},
        style={'description_width': '100px'}
    )

    parcourir_btn = WButton(description="📂 Parcourir Drive", button_style='info')
    ouvrir_dossier_btn = WButton(description="📂 Ouvrir le dossier", button_style='info')
    sauvegarder_btn = WButton(description="✅ Sauvegarder", button_style='primary')
    annuler_btn = WButton(description="❌ Annuler", button_style='danger')

    output_save = Output()

    # Gestionnaires
    def on_parcourir(b):
        logger.debug("Bouton 'Parcourir Drive' cliqué")
        from google.colab import files
        with output_save:
            clear_output(wait=True)
            display(HTML("<i>💡 Pour choisir un dossier, entre le chemin manuellement.</i>"))
            display(HTML("<i>Exemple: /content/drive/MyDrive/MonDossier/</i>"))

    def on_ouvrir_dossier(b):
        dossier = os.path.dirname(chemin_input.value)
        logger.debug(f"Bouton 'Ouvrir dossier' cliqué - Dossier: {dossier}")
        
        if os.path.exists(dossier):
            from IPython.display import Javascript
            display(Javascript(f'window.open("https://colab.research.google.com/notebooks#fileId={dossier}")'))
            with output_save:
                display(HTML(f"<i>📂 Dossier : {dossier}</i>"))
            logger.info(f"📂 Dossier ouvert: {dossier}")
        else:
            logger.warning(f"⚠️ Tentative ouverture dossier inexistant: {dossier}")
            with output_save:
                display(HTML(f"<span style='color:orange'>⚠️ Dossier n'existe pas encore</span>"))

    def on_sauvegarder(b):
        chemin = chemin_input.value.strip()
        logger.info(f"Bouton 'Sauvegarder' cliqué - Chemin: {chemin}")
        
        if sauvegarder_texte(contenu, chemin):
            with output_save:
                clear_output(wait=True)
                display(HTML(f"<span style='color:green'>✅ Sauvegarde réussie !</span>"))
                display(HTML(f"<i>📄 {chemin}</i>"))
                # Proposer de télécharger si fichier externe
                if not chemin.startswith('/content/drive/'):
                    display(HTML("<br>"))
                    download_btn = WButton(description="⬇️ Télécharger le fichier", button_style='info')
                    def on_download(b):
                        logger.debug(f"Téléchargement du fichier: {chemin}")
                        files.download(chemin)
                        logger.info(f"⬇️ Fichier téléchargé: {os.path.basename(chemin)}")
                    download_btn.on_click(on_download)
                    display(download_btn)
        else:
            logger.error(f"❌ Échec sauvegarde vers {chemin}")
            with output_save:
                clear_output(wait=True)
                display(HTML("<span style='color:red'>❌ Erreur lors de la sauvegarde</span>"))

    def on_annuler(b):
        logger.info(f"❌ Sauvegarde annulée par l'utilisateur - Type: {type_generation}")
        with output_save:
            clear_output(wait=True)
            display(HTML("<i>✨ Sauvegarde annulée</i>"))

    parcourir_btn.on_click(on_parcourir)
    ouvrir_dossier_btn.on_click(on_ouvrir_dossier)
    sauvegarder_btn.on_click(on_sauvegarder)
    annuler_btn.on_click(on_annuler)

    # Affichage du message selon le type de source
    if type_source == "drive":
        display(HTML(f"<span style='color:green'>📁 Fichier Drive détecté</span>"))
        display(HTML(f"<i>Dossier d'origine : {dossier_origine}</i>"))
    elif type_source == "externe":
        display(HTML(f"<span style='color:orange'>📁 Fichier externe détecté</span>"))
        display(HTML(f"<i>Un dossier dédié sera créé : {os.path.dirname(chemin_defaut)}</i>"))
    else:
        display(HTML(f"<span style='color:blue'>📝 Texte saisi manuellement</span>"))

    display(HTML("<hr>"))
    display(label_info)
    display(chemin_input)
    display(HBox([parcourir_btn, ouvrir_dossier_btn, sauvegarder_btn, annuler_btn]))
    display(output_save)

logger.info("✅ Module de sauvegarde initialisé")
print("✅ Fonctions de sauvegarde prêtes")