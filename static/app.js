// ========== MODÈLE DE DONNÉES ==========
let workflow = {
    id: null,
    name: "Mon dossier",
    document: "",
    steps: []
};

let currentEditingStepIndex = null;

// Types d'étapes avec leur configuration
const stepTypes = {
    analyse: {
        name: "🔍 Analyser",
        fields: [],
        execute: async (step, context) => {
            return await callApiWithContext('analyser', step, context);
        }
    },
    conclusions: {
        name: "⚖️ Conclusions",
        fields: [],
        execute: async (step, context) => {
            return await callApiWithContext('conclusions', step, context);
        }
    },
    ameliorer: {
        name: "✨ Améliorer",
        fields: [],
        execute: async (step, context) => {
            return await callApiWithContext('ameliorer', step, context);
        }
    },
    email: {
        name: "📧 Email",
        fields: [
            { name: "destinataire", label: "Destinataire", type: "text", placeholder: "client@email.com" },
            { name: "objet", label: "Objet", type: "text", placeholder: "Objet de l'email" },
            { name: "source", label: "Basé sur", type: "select", options: [
                { value: "document", label: "📄 Document source" },
                { value: "analyse", label: "📊 Dernière analyse" },
                { value: "conclusions", label: "⚖️ Dernières conclusions" },
                { value: "recherche", label: "🔍 Dernière recherche" }
            ]}
        ],
        execute: async (step, context) => {
            return await callApiWithContext('email', step, context);
        }
    },
    rediger: {
        name: "📜 Rédiger",
        fields: [
            { name: "acte_type", label: "Type d'acte", type: "select", options: [
                { value: "contrat", label: "Contrat" },
                { value: "avenant", label: "Avenant" },
                { value: "mise_en_demeure", label: "Mise en demeure" },
                { value: "assignation", label: "Assignation" }
            ]},
            { name: "instructions", label: "Instructions", type: "textarea", placeholder: "Instructions spécifiques..." }
        ],
        execute: async (step, context) => {
            return await callApiWithContext('rediger', step, context);
        }
    },
    recherche: {
        name: "🔍 Recherche",
        fields: [
            { name: "query", label: "Question juridique", type: "textarea", placeholder: "Votre question..." }
        ],
        execute: async (step, context) => {
            return await callApiWithContext('recherche', step, context);
        }
    },
    preparer_audience: {
        name: "⚖️ Audience",
        fields: [],
        execute: async (step, context) => {
            return await callApiWithContext('preparer_audience', step, context);
        }
    },
    generer_arguments: {
        name: "🧠 Arguments",
        fields: [],
        execute: async (step, context) => {
            return await callApiWithContext('generer_arguments', step, context);
        }
    },
    generer_prompt: {
        name: "🎯 Prompt",
        fields: [
            { name: "prompt_type", label: "Type de prompt", type: "select", options: [
                { value: "prompt_basic", label: "Prompt basique" },
                { value: "prompt_jurisprudence", label: "Recherche jurisprudence" },
                { value: "prompt_dossier", label: "Analyse dossier" },
                { value: "recherche_nullites", label: "Recherche nullités" }
            ]},
            { name: "situation", label: "Situation juridique", type: "textarea", placeholder: "Décrivez votre situation..." }
        ],
        execute: async (step, context) => {
            return await callApiWithContext('generer_prompt', step, context);
        }
    },
    appliquer_tampon: {
        name: "🖊️ Tampon",
        fields: [
            { name: "nom", label: "Nom", type: "text" },
            { name: "prenom", label: "Prénom", type: "text" },
            { name: "barreau", label: "Barreau", type: "text" }
        ],
        execute: async (step, context) => {
            return await callApiWithContext('appliquer_tampon', step, context);
        }
    }
};

// Stockage des résultats par étape
let stepResults = {};

// ========== FONCTIONS PRINCIPALES ==========

// Ajouter une étape au workflow
function addStep() {
    const stepType = document.getElementById('step_type_select').value;
    const stepConfig = stepTypes[stepType];
    
    const newStep = {
        id: Date.now(),
        type: stepType,
        name: stepConfig.name,
        config: {},
        status: 'pending', // pending, running, success, error
        result: null,
        error: null
    };
    
    // Initialiser la config avec les valeurs par défaut des champs
    if (stepConfig.fields) {
        stepConfig.fields.forEach(field => {
            newStep.config[field.name] = '';
        });
    }
    
    workflow.steps.push(newStep);
    renderWorkflow();
}

// Rendre le workflow dans l'UI
function renderWorkflow() {
    const container = document.getElementById('workflow-steps');
    if (!container) return;
    
    if (workflow.steps.length === 0) {
        container.innerHTML = `
            <div class="empty-workflow">
                <p>✨ Aucune étape dans votre workflow</p>
                <p>Cliquez sur <strong>+ Ajouter une étape</strong> pour commencer</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    workflow.steps.forEach((step, index) => {
        const statusIcon = getStatusIcon(step.status);
        const resultPreview = step.result ? step.result.substring(0, 100) + '...' : '';
        
        html += `
            <div class="workflow-step" data-step-id="${step.id}" data-step-index="${index}">
                <div class="step-header">
                    <div class="step-title">
                        <span class="step-number">${index + 1}.</span>
                        <span class="step-name">${step.name}</span>
                        <span class="step-status ${step.status}">${statusIcon}</span>
                    </div>
                    <div class="step-actions">
                        <button class="icon-btn" onclick="editStep(${index})" title="Configurer">⚙️</button>
                        <button class="icon-btn" onclick="runStep(${index})" title="Exécuter">▶️</button>
                        <button class="icon-btn" onclick="moveStepUp(${index})" ${index === 0 ? 'disabled' : ''}>⬆️</button>
                        <button class="icon-btn" onclick="moveStepDown(${index})" ${index === workflow.steps.length - 1 ? 'disabled' : ''}>⬇️</button>
                        <button class="icon-btn danger" onclick="deleteStep(${index})" title="Supprimer">🗑️</button>
                    </div>
                </div>
                ${step.config && Object.keys(step.config).length > 0 ? `
                    <div class="step-config">
                        ${renderStepConfig(step)}
                    </div>
                ` : ''}
                ${step.result ? `
                    <div class="step-result">
                        <details>
                            <summary>📄 Résultat</summary>
                            <div class="result-content">${escapeHtml(step.result)}</div>
                            <div class="result-actions">
                                <button onclick="copyStepResult(${index})">📋 Copier</button>
                                <button onclick="useAsContext(${index})">📎 Utiliser comme contexte</button>
                            </div>
                        </details>
                    </div>
                ` : ''}
                ${step.error ? `
                    <div class="step-error">
                        ❌ ${escapeHtml(step.error)}
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Exécuter une étape spécifique
async function runStep(stepIndex) {
    const step = workflow.steps[stepIndex];
    const stepDef = stepTypes[step.type];
    
    step.status = 'running';
    step.error = null;
    renderWorkflow();
    
    try {
        // Utiliser la nouvelle fonction avec mode
        const context = getContextForStep(stepIndex);
        
        let finalText = workflow.document;
        if (context) {
            finalText = `${context.result}\n\n[DOCUMENT SOURCE]\n${workflow.document}`;
        }
        
        const apiData = {
            text: finalText,
            config: step.config,
            context: context,
            step_type: step.type
        };
        
        const endpointType = step.type === 'analyse' ? 'analyser' : step.type;
        const result = await callWorkflowStep(endpointType, apiData);
        
        step.status = 'success';
        step.result = result;
        stepResults[step.id] = result;
        
        const mode = document.getElementById('contextMode')?.value === 'full' ? 'complet' : 'dernier résultat';
        showNotification(`✅ ${step.name} terminé (mode: ${mode})`);
        
    } catch (error) {
        step.status = 'error';
        step.error = error.message;
        showNotification(`❌ Erreur: ${error.message}`, 'error');
    }
    
    renderWorkflow();
}

// Exécuter toutes les étapes séquentiellement
async function executeAllSteps() {
    for (let i = 0; i < workflow.steps.length; i++) {
        if (workflow.steps[i].status !== 'success') {
            await runStep(i);
        }
    }
    showNotification('✅ Workflow complété !');
}

// Obtenir le contexte selon le mode choisi
function getContextForStep(stepIndex) {
    if (stepIndex === 0) return null;
    
    const contextMode = document.getElementById('contextMode')?.value || 'full';
    const previousSteps = workflow.steps.slice(0, stepIndex);
    const successfulResults = previousSteps.filter(step => step.result);
    
    if (successfulResults.length === 0) return null;
    
    if (contextMode === 'last') {
        // Mode : seulement le dernier résultat
        const lastStep = successfulResults[successfulResults.length - 1];
        return {
            type: 'last_only',
            result: `[RÉSULTAT PRÉCÉDENT - ${lastStep.name}]\n${lastStep.result}`,
            steps: [lastStep]
        };
    } else {
        // Mode : historique complet
        let contextHistory = "=== HISTORIQUE COMPLET DU WORKFLOW ===\n\n";
        
        successfulResults.forEach((step, idx) => {
            contextHistory += `--- Étape ${idx + 1}: ${step.name} ---\n`;
            contextHistory += `${step.result}\n\n`;
        });
        
        contextHistory += "=== INSTRUCTIONS ===\n";
        contextHistory += "Utilisez l'historique ci-dessus pour répondre.\n";
        
        return {
            type: 'full_history',
            result: contextHistory,
            steps: successfulResults
        };
    }
}


async function callWorkflowStep(stepType, data) {
    let finalText = data.text;
    
    // Si un contexte existe, l'ajouter au texte
    if (data.context && data.context.result) {
        finalText = `[RÉSULTAT PRÉCÉDENT]\n${data.context.result}\n\n[DOCUMENT ORIGINAL]\n${data.text}`;
    }
    
    const endpoint = `/api/${stepType}`;
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ...data,
            text: finalText  // ← Texte enrichi avec le contexte
        })
    });
    
    const result = await response.json();
    if (result.error) throw new Error(result.error);
    return result.result;
}

// Sauvegarder le workflow
async function saveWorkflow() {
    const workflowData = {
        name: workflow.name,
        document: workflow.document,
        steps: workflow.steps.map(step => ({
            type: step.type,
            config: step.config,
            status: step.status,
            result: step.result
        }))
    };
    
    localStorage.setItem('saved_workflow', JSON.stringify(workflowData));
    showNotification('💾 Workflow sauvegardé');
}

// Charger un workflow sauvegardé
function loadWorkflow() {
    const saved = localStorage.getItem('saved_workflow');
    if (saved) {
        const loaded = JSON.parse(saved);
        workflow.name = loaded.name;
        workflow.document = loaded.document;
        workflow.steps = loaded.steps.map(step => ({
            ...step,
            id: Date.now() + Math.random(),
            status: 'pending' // Reset status on load
        }));
        renderWorkflow();
        showNotification('📂 Workflow chargé');
    } else {
        showNotification('Aucun workflow sauvegardé', 'error');
    }
}

// ========== INITIALISATION ==========
document.addEventListener('DOMContentLoaded', () => {
    // Configurer les écouteurs
    document.getElementById('addStepBtn')?.addEventListener('click', addStep);
    document.getElementById('executeAllBtn')?.addEventListener('click', executeAllSteps);
    document.getElementById('saveWorkflowBtn')?.addEventListener('click', saveWorkflow);
    document.getElementById('loadWorkflowBtn')?.addEventListener('click', loadWorkflow);
    document.getElementById('loadDocBtn')?.addEventListener('click', loadDocument);
    document.getElementById('initBtn')?.addEventListener('click', initAssistant);
    
    // Charger les providers
    loadProvidersWithKeys();
    
    // Initialiser le workflow vide
    renderWorkflow();
});

// Helper: Échapper le HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper: Afficher une notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}


// /////////////////// NEW ////////////////////////////////
// ========== FONCTIONS MANQUANTES À AJOUTER ==========

// Fonction pour obtenir l'icône de statut
function getStatusIcon(status) {
    switch(status) {
        case 'pending':
            return '⏳ En attente';
        case 'running':
            return '🔄 En cours...';
        case 'success':
            return '✅ Terminé';
        case 'error':
            return '❌ Erreur';
        default:
            return '⚪ Inconnu';
    }
}

// Fonction pour charger un document (version workflow)
async function loadDocument() {
    const fileInput = document.getElementById('file_upload');
    const textarea = document.getElementById('direct_text');
    const statusDiv = document.getElementById('doc_status');
    const dossierNameSpan = document.getElementById('dossier_name');
    
    const file = fileInput ? fileInput.files[0] : null;
    const directText = textarea ? textarea.value : "";
    
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (statusDiv) statusDiv.innerHTML = '<div class="loading">📤 Upload en cours...</div>';
        
        try {
            const response = await fetch('/api/upload', { method: 'POST', body: formData });
            const result = await response.json();
            
            if (result.success) {
                workflow.document = result.text;
                if (statusDiv) statusDiv.innerHTML = `<div class="success-msg">✅ ${result.filename} chargé (${result.text.length} caractères)</div>`;
                if (dossierNameSpan) dossierNameSpan.textContent = result.filename;
                
                // Mettre à jour l'info dans le workflow
                const dossierInfo = document.querySelector('.dossier-info strong');
                if (dossierInfo) dossierInfo.textContent = result.filename;
                
                showNotification(`📄 Document chargé : ${result.filename}`);
            } else {
                if (statusDiv) statusDiv.innerHTML = `<div class="error">❌ ${result.error}</div>`;
                showNotification(`Erreur: ${result.error}`, 'error');
            }
        } catch(e) {
            if (statusDiv) statusDiv.innerHTML = `<div class="error">❌ ${e.message}</div>`;
            showNotification(`Erreur: ${e.message}`, 'error');
        }
    } 
    else if (directText && directText.trim()) {
        workflow.document = directText;
        if (statusDiv) statusDiv.innerHTML = `<div class="success-msg">✅ Texte direct chargé (${directText.length} caractères)</div>`;
        if (dossierNameSpan) dossierNameSpan.textContent = "Texte direct";
        
        const dossierInfo = document.querySelector('.dossier-info strong');
        if (dossierInfo) dossierInfo.textContent = "Texte direct";
        
        showNotification(`📝 Texte direct chargé (${directText.length} caractères)`);
    } 
    else {
        if (statusDiv) statusDiv.innerHTML = '<div class="error">❌ Aucun document sélectionné</div>';
        showNotification('Aucun document à charger', 'error');
    }
}

// Fonction pour éditer une étape
function editStep(stepIndex) {
    const step = workflow.steps[stepIndex];
    const stepDef = stepTypes[step.type];
    
    currentEditingStepIndex = stepIndex;
    
    const modal = document.getElementById('stepModal');
    const modalTitle = document.getElementById('modal_title');
    const modalFields = document.getElementById('modal_fields');
    
    if (!modal || !modalFields) return;
    
    modalTitle.textContent = `Configurer : ${stepDef.name}`;
    
    // Générer les champs du formulaire
    let fieldsHtml = '';
    if (stepDef.fields && stepDef.fields.length > 0) {
        stepDef.fields.forEach(field => {
            const currentValue = step.config[field.name] || '';
            
            if (field.type === 'select') {
                fieldsHtml += `
                    <label>${field.label}</label>
                    <select id="modal_field_${field.name}">
                        ${field.options.map(opt => `
                            <option value="${opt.value}" ${currentValue === opt.value ? 'selected' : ''}>${opt.label}</option>
                        `).join('')}
                    </select>
                `;
            } else if (field.type === 'textarea') {
                fieldsHtml += `
                    <label>${field.label}</label>
                    <textarea id="modal_field_${field.name}" rows="3" placeholder="${field.placeholder || ''}">${escapeHtml(currentValue)}</textarea>
                `;
            } else {
                fieldsHtml += `
                    <label>${field.label}</label>
                    <input type="${field.type || 'text'}" id="modal_field_${field.name}" value="${escapeHtml(currentValue)}" placeholder="${field.placeholder || ''}">
                `;
            }
        });
    } else {
        fieldsHtml = '<p class="text-muted">Aucune configuration nécessaire pour cette étape.</p>';
    }
    
    modalFields.innerHTML = fieldsHtml;
    modal.style.display = 'block';
}

// Fermer le modal
function closeStepModal() {
    const modal = document.getElementById('stepModal');
    if (modal) modal.style.display = 'none';
    currentEditingStepIndex = null;
}

// Sauvegarder la configuration de l'étape
function saveStepConfig() {
    if (currentEditingStepIndex === null) return;
    
    const step = workflow.steps[currentEditingStepIndex];
    const stepDef = stepTypes[step.type];
    
    if (stepDef.fields && stepDef.fields.length > 0) {
        stepDef.fields.forEach(field => {
            const fieldElement = document.getElementById(`modal_field_${field.name}`);
            if (fieldElement) {
                step.config[field.name] = fieldElement.value;
            }
        });
    }
    
    closeStepModal();
    renderWorkflow();
    showNotification(`✅ Configuration de "${step.name}" enregistrée`);
}

// Déplacer une étape vers le haut
function moveStepUp(stepIndex) {
    if (stepIndex === 0) return;
    const temp = workflow.steps[stepIndex];
    workflow.steps[stepIndex] = workflow.steps[stepIndex - 1];
    workflow.steps[stepIndex - 1] = temp;
    renderWorkflow();
    showNotification('⬆️ Ordre modifié');
}

// Déplacer une étape vers le bas
function moveStepDown(stepIndex) {
    if (stepIndex === workflow.steps.length - 1) return;
    const temp = workflow.steps[stepIndex];
    workflow.steps[stepIndex] = workflow.steps[stepIndex + 1];
    workflow.steps[stepIndex + 1] = temp;
    renderWorkflow();
    showNotification('⬇️ Ordre modifié');
}

// Supprimer une étape
function deleteStep(stepIndex) {
    if (confirm('Supprimer cette étape ?')) {
        workflow.steps.splice(stepIndex, 1);
        renderWorkflow();
        showNotification('🗑️ Étape supprimée');
    }
}

// Copier le résultat d'une étape
function copyStepResult(stepIndex) {
    const step = workflow.steps[stepIndex];
    if (step && step.result) {
        navigator.clipboard.writeText(step.result);
        showNotification('📋 Résultat copié dans le presse-papier');
    }
}

// Utiliser le résultat d'une étape comme contexte pour la suivante
function useAsContext(stepIndex) {
    const step = workflow.steps[stepIndex];
    if (step && step.result) {
        // Stocker dans un contexte global
        window.globalContext = {
            source: step.type,
            content: step.result,
            timestamp: new Date().toISOString()
        };
        showNotification(`📎 Résultat de "${step.name}" disponible comme contexte pour les étapes suivantes`);
        
        // Ajouter un indicateur visuel
        const stepElement = document.querySelector(`.workflow-step[data-step-index="${stepIndex}"]`);
        if (stepElement) {
            stepElement.style.borderLeft = '3px solid #ffc107';
            setTimeout(() => {
                stepElement.style.borderLeft = '';
            }, 2000);
        }
    }
}

// Rendre la configuration d'une étape (pour l'affichage)
function renderStepConfig(step) {
    const stepDef = stepTypes[step.type];
    if (!stepDef.fields || stepDef.fields.length === 0) return '';
    
    let html = '<div class="step-config-details">';
    stepDef.fields.forEach(field => {
        const value = step.config[field.name];
        if (value && value.trim()) {
            html += `
                <div class="config-item">
                    <strong>${field.label}:</strong> 
                    <span>${escapeHtml(value.length > 50 ? value.substring(0, 50) + '...' : value)}</span>
                </div>
            `;
        }
    });
    html += '</div>';
    return html;
}

// Initialiser l'assistant (version workflow)
async function initAssistant() {
    const providerName = document.getElementById('provider_select').value;
    const modelKey = document.getElementById('model_select').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('max_tokens').value);
    const statusDiv = document.getElementById('init_status');
    
    if (!providerName) {
        alert('Veuillez d\'abord sélectionner un provider');
        return;
    }
    
    if (!modelKey) {
        alert('Veuillez sélectionner un modèle');
        return;
    }
    
    if (statusDiv) statusDiv.innerHTML = '<div class="loading">Initialisation...</div>';
    
    try {
        const response = await fetch('/api/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider_name: providerName,
                model_key: modelKey,
                temperature: temperature,
                max_tokens: maxTokens
            })
        });
        const result = await response.json();
        
        if (result.success) {
            if (statusDiv) statusDiv.innerHTML = `<div class="success-msg">✅ Assistant initialisé avec ${result.model_display}</div>`;
            showNotification(`🚀 Assistant prêt : ${result.model_display}`);
        } else {
            if (statusDiv) statusDiv.innerHTML = `<div class="error">❌ ${result.error}</div>`;
            showNotification(`Erreur: ${result.error}, Detail: ${result.body}` , 'error');
        }
    } catch(e) {
        if (statusDiv) statusDiv.innerHTML = `<div class="error">❌ ${e.message}</div>`;
        showNotification(`Erreur: ${e.message}`, 'error');
    }
}

// Mettre à jour la fonction renderWorkflow pour utiliser getStatusIcon
// (Assurez-vous que renderWorkflow utilise bien getStatusIcon)

// Recharger les providers (version workflow)
async function loadProvidersWithKeys() {
    try {
        const response = await fetch('/api/providers/with_keys');
        const providers = await response.json();
        const select = document.getElementById('provider_select');
        if (!select) return;
        
        select.innerHTML = '<option value="">-- Sélectionner un provider --</option>';
        
        if (providers.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.disabled = true;
            opt.textContent = "Aucun provider - Configurez vos clés dans l'onglet Configuration";
            select.appendChild(opt);
        } else {
            providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider.name;
                const modelText = provider.models_count === 1 ? 'modèle' : 'modèles';
                option.textContent = `${provider.name} (${provider.models_count} ${modelText})`;
                select.appendChild(option);
            });
        }
    } catch(e) {
        console.error('Error loading providers:', e);
        const select = document.getElementById('provider_select');
        if (select) select.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

// Charger les modèles quand on change de provider
async function loadModelsForProviderSelect() {
    const providerName = document.getElementById('provider_select').value;
    const modelSelect = document.getElementById('model_select');
    
    if (!providerName) {
        modelSelect.innerHTML = '<option value="">-- Sélectionnez d\'abord un provider --</option>';
        modelSelect.disabled = true;
        return;
    }
    
    modelSelect.innerHTML = '<option value="">Chargement...</option>';
    modelSelect.disabled = true;
    
    try {
        const response = await fetch('/api/models/available/' + encodeURIComponent(providerName));
        const models = await response.json();
        
        modelSelect.innerHTML = '<option value="">-- Sélectionner un modèle --</option>';
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.model_key;
            option.textContent = model.display_name + ' (' + model.context_length + ' tokens)';
            modelSelect.appendChild(option);
        });
        modelSelect.disabled = false;
    } catch(e) {
        modelSelect.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

// Ajoutez ceci au début, près de workflow
let workflowHistory = {
    steps: [],           // Historique de toutes les étapes exécutées
    currentContext: null // Contexte cumulé
};

// Afficher l'interface de configuration dans un modal simple
function showConfigModal() {
    const modalHtml = `
        <div id="simpleConfigModal" class="modal" style="display:block">
            <div class="modal-content" style="width:700px; max-width:90%">
                <span class="close" onclick="closeModal('simpleConfigModal')">&times;</span>
                <h3>🔧 Configuration des providers</h3>
                <div id="simpleConfigContent">Chargement...</div>
            </div>
        </div>
    `;
    
    // Ajouter le modal au body s'il n'existe pas
    if (!document.getElementById('simpleConfigModal')) {
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    } else {
        document.getElementById('simpleConfigModal').style.display = 'block';
    }
    
    // Charger le contenu
    loadSimpleConfigContent();
}

async function loadSimpleConfigContent() {
    const container = document.getElementById('simpleConfigContent');
    if (!container) return;
    
    try {
        // Charger les providers
        const providersRes = await fetch('/api/providers/list');
        const providers = await providersRes.json();
        
        let html = '<h4>📋 Providers existants</h4>';
        html += '<table style="width:100%; margin-bottom:20px; border-collapse:collapse">';
        html += '<thead><tr style="background:#f0f2f6"><th>Nom</th><th>URL</th><th>API Key</th><th>Actions</th></tr></thead><tbody>';
        
        for (const p of providers) {
            const maskedKey = p.api_key ? '•••' + p.api_key.slice(-6) : '❌ Non configurée';
            html += `
                <tr style="border-bottom:1px solid #ddd">
                    <td style="padding:8px"><strong>${p.name}</strong></td>
                    <td style="padding:8px">${p.url}</td>
                    <td style="padding:8px">${maskedKey}</td>
                    <td style="padding:8px">
                        <button onclick="editProviderKey('${p.name}')" style="margin:2px">✏️ Clé</button>
                        <button onclick="showAddModelForm('${p.name}')" style="margin:2px">➕ Modèle</button>
                        <button onclick="deleteProviderSimple('${p.name}')" class="danger" style="margin:2px">🗑️</button>
                    </td>
                </tr>
            `;
        }
        html += '</tbody></table>';
        
        // Formulaire pour ajouter un provider
        html += '<hr><h4>➕ Ajouter un provider</h4>';
        html += '<div style="display:flex; gap:10px; flex-wrap:wrap">';
        html += '<input type="text" id="newProviderName" placeholder="Nom (ex: deepseek)" style="flex:1">';
        html += '<input type="text" id="newProviderUrl" placeholder="URL API" style="flex:2">';
        html += '<input type="password" id="newProviderKey" placeholder="API Key (optionnel)" style="flex:1">';
        html += '<button onclick="addProviderSimple()" class="success">➕ Ajouter provider</button>';
        html += '</div>';
        
        // Modèles disponibles
        html += '<hr><h4>📚 Modèles disponibles</h4>';
        html += '<div id="simpleModelsList">Chargement...</div>';
        
        container.innerHTML = html;
        
        // Charger les modèles
        const modelsRes = await fetch('/api/providers/with_keys');
        const providersWithKeys = await modelsRes.json();
        
        let modelsHtml = '<table style="width:100%; border-collapse:collapse"><thead><tr style="background:#f0f2f6"><th>Provider</th><th>Modèles</th></tr></thead><tbody>';
        
        for (const p of providersWithKeys) {
            const modelRes = await fetch(`/api/models/list/${p.name}`);
            const models = await modelRes.json();
            
            if (models.length > 0) {
                modelsHtml += `<tr style="border-bottom:1px solid #ddd"><td style="padding:8px"><strong>${p.name}</strong></td><td style="padding:8px">`;
                models.forEach(m => {
                    modelsHtml += `<div>📌 ${m.display_name} (${m.context_length} tokens)</div>`;
                });
                modelsHtml += `</td></tr>`;
            }
        }
        
        modelsHtml += '</tbody></table>';
        document.getElementById('simpleModelsList').innerHTML = modelsHtml;
        
    } catch(e) {
        console.error('Erreur:', e);
        container.innerHTML = '<div class="error">❌ Erreur de chargement: ' + e.message + '</div>';
    }
}

async function addProviderSimple() {
    const name = document.getElementById('newProviderName')?.value.trim();
    const url = document.getElementById('newProviderUrl')?.value.trim();
    const apiKey = document.getElementById('newProviderKey')?.value;
    
    if (!name || !url) {
        alert('Nom et URL requis');
        return;
    }
    
    const res = await fetch('/api/providers/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, url, api_key: apiKey })
    });
    const result = await res.json();
    
    if (result.success) {
        alert('Provider ajouté');
        closeModal('simpleConfigModal');
        loadProvidersWithKeys();  // Rafraîchir la sidebar
    } else {
        alert('Erreur: ' + result.message);
    }
}

async function editProviderKey(providerName) {
    const newKey = prompt(`Nouvelle API key pour ${providerName}:`);
    if (newKey !== null) {
        const res = await fetch('/api/providers/update_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: providerName, api_key: newKey })
        });
        const result = await res.json();
        if (result.success) {
            alert('Clé mise à jour');
            loadSimpleConfigContent();
            loadProvidersWithKeys();
        } else {
            alert('Erreur: ' + result.message);
        }
    }
}

async function deleteProviderSimple(providerName) {
    if (confirm(`Supprimer ${providerName} ?`)) {
        const res = await fetch('/api/providers/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: providerName })
        });
        const result = await res.json();
        if (result.success) {
            alert('Provider supprimé');
            loadSimpleConfigContent();
            loadProvidersWithKeys();
        } else {
            alert('Erreur: ' + result.message);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

document.getElementById('showConfigBtn')?.addEventListener('click', showConfigModal);

// Afficher le formulaire pour ajouter un modèle
function showAddModelForm(providerName) {
    const modal = document.getElementById('simpleConfigModal');
    const container = document.getElementById('simpleConfigContent');
    
    if (!modal || !container) return;
    
    const formHtml = `
        <h3>➕ Ajouter un modèle pour ${providerName}</h3>
        <div style="margin-top: 15px">
            <label>Clé modèle:</label>
            <input type="text" id="newModelKey" placeholder="ex: gemini-2.0-flash" style="width:100%; margin-bottom:10px">
            
            <label>Nom affiché:</label>
            <input type="text" id="newModelDisplayName" placeholder="ex: Gemini 2.0 Flash" style="width:100%; margin-bottom:10px">
            
            <label>Contexte (tokens):</label>
            <input type="number" id="newModelContext" placeholder="ex: 1048576" style="width:100%; margin-bottom:10px">
            
            <div style="display:flex; gap:10px; margin-top:15px">
                <button onclick="addModelToProvider('${providerName}')" class="success">✅ Ajouter</button>
                <button onclick="loadSimpleConfigContent()" class="danger">Annuler</button>
            </div>
        </div>
    `;
    
    container.innerHTML = formHtml;
}

// Ajouter un modèle à un provider
async function addModelToProvider(providerName) {
    const modelKey = document.getElementById('newModelKey')?.value.trim();
    const displayName = document.getElementById('newModelDisplayName')?.value.trim();
    const contextLength = parseInt(document.getElementById('newModelContext')?.value);
    
    if (!modelKey || !displayName || !contextLength) {
        alert('Tous les champs sont requis');
        return;
    }
    
    const res = await fetch('/api/models/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            provider_name: providerName,
            model_key: modelKey,
            display_name: displayName,
            context_length: contextLength
        })
    });
    
    const result = await res.json();
    
    if (result.success) {
        alert(`✅ Modèle ${displayName} ajouté avec succès`);
        // Rafraîchir la vue
        loadSimpleConfigContent();
        loadProvidersWithKeys();
    } else {
        alert('❌ Erreur: ' + result.message);
    }
}