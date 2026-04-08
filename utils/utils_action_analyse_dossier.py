from pypdf import PdfReader
import os
import docx
from utils.utils_logging import get_logger

logger = get_logger(__name__)


# 📄 EXTRACTION PDF
def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un fichier PDF"""
    
    logger.info(f"📄 Extraction PDF: {file_path}")
    
    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"⚠️ Erreur extraction page: {str(e)}")
                continue

        if not text.strip():
            logger.warning(f"⚠️ Aucun texte extrait du PDF: {file_path}")

        logger.info(f"✅ Extraction réussie - {len(text)} caractères")
        return text

    except FileNotFoundError:
        logger.error(f"❌ Fichier PDF introuvable: {file_path}")
        return ""
    except PermissionError:
        logger.error(f"❌ Permission refusée pour: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"❌ Erreur extraction PDF: {str(e)}")
        return ""


# 📄 EXTRACTION DOCX
def extract_text_from_docx(file_path: str) -> str:
    """Extrait le texte d'un fichier DOCX"""
    
    logger.info(f"📄 Extraction DOCX: {file_path}")
    
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        if not text.strip():
            logger.warning(f"⚠️ Aucun texte extrait du DOCX: {file_path}")
        
        logger.info(f"✅ Extraction réussie - {len(text)} caractères")
        return text
        
    except FileNotFoundError:
        logger.error(f"❌ Fichier DOCX introuvable: {file_path}")
        return ""
    except PermissionError:
        logger.error(f"❌ Permission refusée pour: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"❌ Erreur extraction DOCX: {str(e)}")
        return ""


# 📄 EXTRACTION TXT
def extract_text_from_txt(file_path: str) -> str:
    """Extrait le texte d'un fichier TXT"""
    
    logger.info(f"📄 Extraction TXT: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            logger.warning(f"⚠️ Aucun texte extrait du TXT: {file_path}")
        
        logger.info(f"✅ Extraction réussie - {len(text)} caractères")
        return text
        
    except FileNotFoundError:
        logger.error(f"❌ Fichier TXT introuvable: {file_path}")
        return ""
    except UnicodeDecodeError:
        # Essayer avec un autre encodage
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            logger.info(f"✅ Extraction avec latin-1 - {len(text)} caractères")
            return text
        except Exception as e:
            logger.error(f"❌ Erreur décodage TXT: {str(e)}")
            return ""
    except PermissionError:
        logger.error(f"❌ Permission refusée pour: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"❌ Erreur extraction TXT: {str(e)}")
        return ""


# 📄 EXTRACTION MULTI-FORMATS (FONCTION PRINCIPALE)
def extract_text_from_file(file_path: str) -> str:
    """Extrait le texte d'un fichier selon son extension"""
    
    if not os.path.exists(file_path):
        logger.error(f"❌ Fichier introuvable: {file_path}")
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return extract_text_from_docx(file_path)
        elif ext == '.txt':
            return extract_text_from_txt(file_path)
        else:
            logger.warning(f"⚠️ Format non supporté: {ext} pour {file_path}")
            return f"❌ Format non supporté: {ext}"
            
    except Exception as e:
        logger.error(f"❌ Erreur inattendue extraction {file_path}: {str(e)}")
        return ""


# ✂️ CHUNKING
def split_text(text: str, chunk_size=2000, overlap=200) -> list:
    """Découpe le texte en chunks"""
    
    if not text:
        logger.warning("⚠️ Texte vide pour split")
        return []

    try:
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap

        logger.info(f"✂️ Texte découpé en {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"❌ Erreur chunking: {str(e)}")
        return []


# 🧠 ANALYSE D'UN CHUNK
def analyze_chunk(chunk: str, llm_client) -> str:
    """Analyse un segment de texte juridique"""

    if not chunk or not chunk.strip():
        logger.warning("⚠️ Chunk vide ignoré")
        return ""

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return ""

    prompt = f"""
Analyse ce passage d’un dossier juridique et extrais :
- faits importants
- éléments juridiques
- points de tension

Texte :
{chunk[:6000]}
"""

    system_prompt = "Tu es un avocat expert en droit français."
    modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None

    if not modele_actif:
        logger.error("❌ Aucun modèle actif")
        return ""

    try:
        result = llm_client.call_llm(
            prompt,
            system_prompt,
            modele_actif,
            temperature=0.3
        )

        if not result:
            logger.error("❌ Résultat None")
            return ""

        if result.get("error"):
            logger.error(f"❌ Erreur API: {result['error']}")
            return ""

        content = result.get("content", "")
        if not content:
            logger.warning("⚠️ Contenu vide retourné")
            
        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout analyse chunk: {str(e)}")
        return ""
    except ConnectionError as e:
        logger.error(f"❌ Erreur connexion: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"❌ Exception analyse chunk: {str(e)}")
        return ""


# 🧩 SYNTHÈSE GLOBALE
def synthesize_analysis(all_chunks_analysis: list, llm_client) -> str:
    """Construit la synthèse globale du dossier"""

    logger.info(f"🧠 Synthèse globale - {len(all_chunks_analysis)} chunks")

    if not all_chunks_analysis:
        logger.error("❌ Aucune analyse à synthétiser")
        return "❌ Erreur: Aucune analyse disponible"

    combined = "\n\n".join([c for c in all_chunks_analysis if c and c.strip()])

    if not combined.strip():
        logger.error("❌ Aucun contenu à synthétiser")
        return "❌ Erreur: Analyse vide"

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return "❌ Erreur: Client LLM non disponible"

    prompt = f"""
À partir des analyses suivantes, construis une synthèse complète du dossier.

Fournis :

1. Résumé global du dossier
2. Chronologie des faits
3. Parties en présence
4. Points juridiques clés
5. Forces du dossier
6. Faiblesses / risques
7. Arguments adverses probables
8. Stratégie recommandée

Analyses :
{combined[:12000]}
"""

    system_prompt = "Tu es un avocat expert en droit français."
    modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None

    if not modele_actif:
        logger.error("❌ Aucun modèle actif")
        return "❌ Erreur: Aucun modèle actif"

    try:
        result = llm_client.call_llm(
            prompt,
            system_prompt,
            modele_actif,
            temperature=0.3
        )

        if not result:
            logger.error("❌ Résultat None")
            return "❌ Erreur: Aucun résultat"

        if result.get("error"):
            logger.error(f"❌ Erreur synthèse: {result['error']}")
            return f"❌ Erreur: {result['error']}"

        content = result.get("content", "")
        
        if not content:
            logger.warning("⚠️ Contenu synthèse vide")
            return "⚠️ Aucune synthèse générée"
        
        logger.info(f"✅ Synthèse générée - {len(content)} caractères")
        return content

    except TimeoutError as e:
        logger.error(f"❌ Timeout synthèse: {str(e)}")
        return "❌ Erreur: Délai dépassé"
    except ConnectionError as e:
        logger.error(f"❌ Erreur connexion: {str(e)}")
        return "❌ Erreur: Problème de connexion"
    except Exception as e:
        logger.error(f"❌ Exception synthèse: {str(e)}")
        return f"❌ Erreur: {str(e)}"


# 🚀 ANALYSE COMPLÈTE DOSSIER
def analyse_dossier(pdf_paths: list, llm_client) -> str:
    """Pipeline complet d'analyse d'un dossier juridique"""

    logger.info(f"⚖️ Analyse dossier - {len(pdf_paths)} fichier(s)")

    # Vérifications initiales
    if not pdf_paths:
        logger.error("❌ Aucun fichier fourni")
        return "❌ Erreur: Aucun fichier fourni"

    if not llm_client:
        logger.error("❌ Client LLM non disponible")
        return "❌ Erreur: Client LLM non disponible"

    try:
        # 1. Extraction multi-format
        all_text = ""
        failed_files = []
        
        for path in pdf_paths:
            text = extract_text_from_file(path)
            if text:
                all_text += text + "\n\n"
            else:
                failed_files.append(os.path.basename(path))

        if failed_files:
            logger.warning(f"⚠️ {len(failed_files)} fichier(s) non extraits: {failed_files}")

        if not all_text.strip():
            logger.error("❌ Aucun texte extrait")
            return "❌ Erreur: Impossible d'extraire le contenu des fichiers"

        logger.info(f"📝 Texte total extrait: {len(all_text)} caractères")

        # 2. Chunking
        chunks = split_text(all_text)

        if not chunks:
            logger.error("❌ Aucun chunk généré")
            return "❌ Erreur: Échec du découpage du texte"

        logger.info(f"📊 {len(chunks)} chunks à analyser")

        # 3. Analyse par chunk
        chunk_analyses = []
        for i, chunk in enumerate(chunks):
            logger.info(f"🔍 Analyse chunk {i+1}/{len(chunks)}")
            try:
                analysis = analyze_chunk(chunk, llm_client)
                if analysis and analysis.strip():
                    chunk_analyses.append(analysis)
                else:
                    logger.warning(f"⚠️ Chunk {i+1} analyse vide")
            except Exception as e:
                logger.error(f"❌ Erreur chunk {i+1}: {str(e)}")
                continue

        if not chunk_analyses:
            logger.error("❌ Aucune analyse valide")
            return "❌ Erreur: Analyse des chunks échouée"

        logger.info(f"✅ {len(chunk_analyses)} analyses valides")

        # 4. Synthèse finale
        final_analysis = synthesize_analysis(chunk_analyses, llm_client)

        return final_analysis

    except Exception as e:
        logger.error(f"❌ Exception analyse dossier: {str(e)}", exc_info=True)
        return f"❌ Erreur inattendue: {str(e)}"