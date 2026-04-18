from flask import Flask, request, jsonify, render_template
import os
import sys
from pathlib import Path
import io
import yaml

sys.path.append(str(Path(__file__).parent))

# ========== IMPORTS DE VOS MODULES ==========
from utils.utils_action_analyser_document import analyser_document
from utils.utils_action_preparer_conclusion import preparer_conclusion
from utils.utils_action_ameliorer_redaction import ameliorer_redaction
from utils.utils_action_preparer_email import preparer_email
from utils.utils_action_rediger_acte import rediger_acte_juridique
from utils.utils_action_analyse_dossier import analyse_dossier
from utils.utils_action_prepare_audience import prepare_audience
from utils.utils_action_simuler_adversaire import simuler_adversaire
from utils.utils_action_generer_prompt import genere_prompt
from utils.utils_recherche_genial import rechercher_dalloz
from utils.utils_tampon import appliquer_tampon
from utils.config_clients import LLM_Client
from utils.db_manager import *
from utils.db_manager import init_database

# Initialize database on startup
init_database()
app = Flask(__name__, static_folder="./static", template_folder="./templates")

# ========== VARIABLES GLOBALES ==========
llm_client = None
templates = {}

# Chargement des templates YAML
try:
    with open("config/prompts.yaml", 'r', encoding='utf-8') as f:
        templates = yaml.safe_load(f)
except Exception as e:
    print("Error loading prompts.yaml:", e)
    templates = {}

# ========== FONCTION DE LECTURE DE FICHIERS ==========
def read_file_content(content, filename):
    """Lit le contenu d'un fichier uploadé"""
    extension = filename.split('.')[-1].lower()
    try:
        if extension == 'txt':
            return content.decode('utf-8')
        elif extension == 'pdf':
            import PyPDF2
            pdf_file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            texts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
            return "\n".join(texts)
        
        elif extension == 'docx':
            import docx
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return f"Format non supporté: {extension}"
    except Exception as e:
        return f"Erreur: {str(e)}"
    

@app.route('/api/providers/list', methods=['GET'])
def api_providers_list():
    """Get all providers"""
    providers = get_all_providers()
    return jsonify(providers)

@app.route('/api/providers/with_keys', methods=['GET'])
def api_providers_with_keys():
    """Get all providers that have API keys configured"""
    conn = get_db_connection()
    providers = conn.execute("""
        SELECT p.name, p.url, 
               COUNT(m.model_key) as models_count
        FROM providers p
        LEFT JOIN models m ON p.name = m.provider_name
        WHERE p.api_key IS NOT NULL AND p.api_key != ''
        GROUP BY p.name
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return jsonify([dict(provider) for provider in providers])

@app.route('/api/providers/add', methods=['POST'])
def api_providers_add():
    """Add a new provider"""
    data = request.json
    success, message = insert_provider(
        name=data['name'],
        url=data['url'],
        api_key=data.get('api_key')
    )
    return jsonify({'success': success, 'message': message})

@app.route('/api/providers/delete', methods=['DELETE'])
def api_providers_delete():
    """Delete a provider"""
    data = request.json
    success, message = delete_provider(data['name'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/providers/update_api_key', methods=['POST'])
def api_providers_update_api_key():
    """Update provider's API key"""
    data = request.json
    success, message = update_provider_api_key(data['name'], data['api_key'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/models/list/<provider_name>', methods=['GET'])
def api_models_list(provider_name):
    """Get models for a provider"""
    models = get_models_by_provider(provider_name)
    return jsonify(models)

@app.route('/api/models/available/<provider_name>', methods=['GET'])
def api_models_available_by_provider(provider_name):
    """Get available models for a specific provider"""
    conn = get_db_connection()
    provider = conn.execute("""
        SELECT api_key FROM providers WHERE name = ? AND api_key IS NOT NULL AND api_key != ''
    """, (provider_name,)).fetchone()
    
    if not provider:
        conn.close()
        return jsonify([])
    
    models = conn.execute("""
        SELECT model_key, display_name, context_length
        FROM models
        WHERE provider_name = ?
        ORDER BY display_name
    """, (provider_name,)).fetchall()
    
    conn.close()
    return jsonify([dict(model) for model in models])

@app.route('/api/models/add', methods=['POST'])
def api_models_add():
    """Add a new model"""
    data = request.json
    success, message = insert_model(
        model_key=data['model_key'],
        provider_name=data['provider_name'],
        display_name=data['display_name'],
        context_length=data['context_length']
    )
    return jsonify({'success': success, 'message': message})

@app.route('/api/models/delete', methods=['DELETE'])
def api_models_delete():
    """Delete a model"""
    data = request.json
    success, message = delete_model(data['model_key'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/init', methods=['POST'])
def init_assistant():
    global llm_client
    data = request.json
    
    conn = get_db_connection()
    model_info = conn.execute("""
        SELECT m.model_key, m.provider_name, m.display_name, p.api_key, p.url
        FROM models m
        JOIN providers p ON m.provider_name = p.name
        WHERE m.provider_name = ? AND m.model_key = ?
    """, (data['provider_name'], data['model_key'])).fetchone()
    conn.close()
    
    if not model_info:
        return jsonify({'success': False, 'error': 'Model not found'})
    
    if not model_info['api_key'] or model_info['api_key'] == '':
        return jsonify({'success': False, 'error': f'API key not configured for provider {model_info["provider_name"]}'})
    
    try:
        llm_client = LLM_Client(
            provider=model_info['provider_name'],
            api_key=model_info['api_key'],
            model=model_info['model_key'],
            temperature=data['temperature'],
            max_tokens=data['max_tokens']
        )
        return jsonify({
            'success': True,
            'model_display': model_info['display_name']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def index():
    return render_template("index.html", templates=templates)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nom vide'})
    content = read_file_content(file.read(), file.filename)
    return jsonify({'success': True, 'text': content, 'filename': file.filename, 'length': len(content)})

@app.route('/api/analyser', methods=['POST'])
def api_analyser():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = analyser_document(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/conclusions', methods=['POST'])
def api_conclusions():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = preparer_conclusion(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ameliorer', methods=['POST'])
def api_ameliorer():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = ameliorer_redaction(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/email', methods=['POST'])
def api_email():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = preparer_email(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/rediger', methods=['POST'])
def api_rediger():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = rediger_acte_juridique(
            data['text'], llm_client,
            data.get('acte_type', 'contrat'),
            data.get('instructions', '')
        )
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/recherche', methods=['POST'])
def api_recherche():
    data = request.json
    try:
        query = data.get('query', data.get('text', ''))
        result = rechercher_dalloz(query)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analyse_dossier', methods=['POST'])
def api_analyse_dossier():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    try:
        files = request.files.getlist('files')
        documents = []
        for file in files:
            content = read_file_content(file.read(), file.filename)
            documents.append(content)
        result = analyse_dossier(documents, llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/preparer_audience', methods=['POST'])
def api_preparer_audience():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = prepare_audience(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/generer_arguments', methods=['POST'])
def api_generer_arguments():
    global llm_client
    if not llm_client:
        return jsonify({'error': 'Assistant non initialise'})
    data = request.json
    try:
        result = simuler_adversaire(data['text'], llm_client)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/generer_prompt', methods=['POST'])
def api_generer_prompt():
    data = request.json
    try:
        result = genere_prompt(data['prompt_type'], data['situation'], templates)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/appliquer_tampon', methods=['POST'])
def api_appliquer_tampon():
    data = request.json
    try:
        result = appliquer_tampon(data['text'], data['config'])
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with Werkzeug Server')
    func()
    return 'Server shutting down...'

if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)