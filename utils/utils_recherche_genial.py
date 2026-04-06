# ========== FONCTION RECHERCHE DALLOZ ==========
import urllib.parse
from IPython.display import display, HTML
from utils.utils_logging import get_logger

logger = get_logger(__name__)

def rechercher_dalloz(texte_original, max_caracteres=300):
    """
    Ouvre une recherche Lefebvre Dalloz avec le texte pertinent
    
    Args:
        texte_original: Texte à rechercher
        max_caracteres: Nombre maximum de caractères pour la recherche
    
    Returns:
        Widget HTML avec boutons de recherche
    """
    
    # Log de début
    logger.info(f"🔍 Recherche Dalloz demandée - Texte original: {len(texte_original)} caractères")
    
    # Vérification des entrées
    if not texte_original or not texte_original.strip():
        logger.warning("⚠️ Texte vide fourni pour la recherche Dalloz")
        return HTML("<div style='color:orange; padding:10px;'>⚠️ Aucun texte à rechercher</div>")
    
    try:
        # 1. Nettoyer le texte
        texte_net = texte_original.strip().replace('\n', ' ').replace('\r', ' ')
        texte_net = ' '.join(texte_net.split())
        logger.debug(f"Texte nettoyé: {len(texte_net)} caractères")
        
        # 2. Tronquer si nécessaire
        original_len = len(texte_net)
        if len(texte_net) > max_caracteres:
            texte_net = texte_net[:max_caracteres]
            dernier_espace = texte_net.rfind(' ')
            if dernier_espace > 0:
                texte_net = texte_net[:dernier_espace]
            texte_net += "..."
            logger.debug(f"Texte tronqué: {original_len} → {len(texte_net)} caractères")
        
        # 3. Encoder l'URL
        query_encodee = urllib.parse.quote(texte_net, safe='')
        url = f"https://genial-for-search.lefebvre-dalloz.fr/"
        
        logger.debug(f"URL générée: {url}")
        logger.debug(f"Query encodée: {query_encodee[:50]}...")
        
        # 4. Générer le HTML
        html_result = f"""
        <div style='background:#f0f4ff; padding:15px; border-radius:8px; border-left:4px solid #1a73e8; margin:10px 0;'>
            <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
                <span style='font-size:24px;'>🔍</span>
                <strong style='color:#1a73e8;'>Recherche Lefebvre Dalloz</strong>
            </div>
            <div style='background:white; padding:10px; border-radius:5px; margin:10px 0; font-size:12px; color:#666;'>
                <strong>Recherche :</strong> {texte_net[:200]}...
            </div>
            <div style='display:flex; gap:10px;'>
                <button
                    onclick="window.open('{url}', '_blank', 'width=1200,height=800,toolbar=yes,menubar=yes')"
                    style='background:#1a73e8; color:white; border:none; padding:8px 16px; border-radius:5px; cursor:pointer;'>
                    📚 Ouvrir Lefebvre Dalloz
                </button>
                <button
                    onclick="navigator.clipboard.writeText(`{texte_net.replace('`', '\\`')}`)"
                    style='background:#f1f3f4; color:#1a73e8; border:1px solid #dadce0; padding:8px 16px; border-radius:5px; cursor:pointer;'>
                    📋 Copier le texte
                </button>
            </div>
            <small style='color:#666; display:block; margin-top:10px;'>
                💡 Astuce : Collez le texte dans la barre de recherche Dalloz
            </small>
        </div>
        """
        
        logger.info(f"✅ Widget Dalloz généré - Texte: {len(texte_net)} caractères")
        return HTML(html_result)
        
    except urllib.parse.quote as e:
        logger.error(f"❌ Erreur d'encodage URL: {str(e)}")
        return HTML("<div style='color:red; padding:10px;'>❌ Erreur technique lors de la préparation de la recherche</div>")
        
    except Exception as e:
        logger.error(f"❌ Exception inattendue dans rechercher_dalloz: {str(e)}")
        logger.debug(f"Détails exception: {type(e).__name__}", exc_info=True)
        return HTML(f"<div style='color:red; padding:10px;'>❌ Erreur: {str(e)}</div>")