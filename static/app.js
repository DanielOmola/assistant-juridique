console.log('=== VÉRIFICATION DES FONCTIONS ===');
console.log('addStep:', typeof addStep);
console.log('executeAllSteps:', typeof executeAllSteps);
console.log('loadDocument:', typeof loadDocument);
console.log('initAssistant:', typeof initAssistant);
console.log('openGestionnaireFlux:', typeof openGestionnaireFlux);
console.log('showConfigModal:', typeof showConfigModal);
console.log('quitApp:', typeof quitApp);
console.log('loadPaths:', typeof loadPaths);
console.log('loadProvidersWithKeys:', typeof loadProvidersWithKeys);
console.log('renderWorkflow:', typeof renderWorkflow);
console.log('==================================');

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
    // function renderWorkflow() {
    //     const container = document.getElementById('workflow-steps');
    //     if (!container) return;
        
    //     if (workflow.steps.length === 0) {
    //         container.innerHTML = `
    //             <div class="empty-workflow">
    //                 <p>✨ Aucune étape dans votre workflow</p>
    //                 <p>Cliquez sur <strong>+ Ajouter une étape</strong> pour commencer</p>
    //             </div>
    //         `;
    //         return;
    //     }
        
    //     let html = '';
    //     workflow.steps.forEach((step, index) => {
    //         const statusIcon = getStatusIcon(step.status);
    //         const resultPreview = step.result ? step.result.substring(0, 100) + '...' : '';
            
    //         html += `
    //             <div class="workflow-step" data-step-id="${step.id}" data-step-index="${index}">
    //                 <div class="step-header">
    //                     <div class="step-title">
    //                         <span class="step-number">${index + 1}.</span>
    //                         <span class="step-name">${step.name}</span>
    //                         <span class="step-status ${step.status}">${statusIcon}</span>
    //                     </div>
    //                     <div class="step-actions">
    //                         <button class="icon-btn" onclick="editStep(${index})" title="Configurer">⚙️</button>
    //                         <button class="icon-btn" onclick="runStep(${index})" title="Exécuter">▶️</button>
    //                         <button class="icon-btn" onclick="moveStepUp(${index})" ${index === 0 ? 'disabled' : ''}>⬆️</button>
    //                         <button class="icon-btn" onclick="moveStepDown(${index})" ${index === workflow.steps.length - 1 ? 'disabled' : ''}>⬇️</button>
    //                         <button class="icon-btn danger" onclick="deleteStep(${index})" title="Supprimer">🗑️</button>
    //                     </div>
    //                 </div>
    //                 ${step.config && Object.keys(step.config).length > 0 ? `
    //                     <div class="step-config">
    //                         ${renderStepConfig(step)}
    //                     </div>
    //                 ` : ''}
    //                 ${step.result ? `
    //                     <div class="step-result">
    //                         <details>
    //                             <summary>📄 Résultat</summary>
    //                             <div class="result-content">${escapeHtml(step.result)}</div>
    //                             <div class="result-actions">
    //                                 <button onclick="copyStepResult(${index})">📋 Copier</button>
    //                                 <button onclick="useAsContext(${index})">📎 Utiliser comme contexte</button>
    //                             </div>
    //                         </details>
    //                     </div>
    //                 ` : ''}
    //                 ${step.error ? `
    //                     <div class="step-error">
    //                         ❌ ${escapeHtml(step.error)}
    //                     </div>
    //                 ` : ''}
    //             </div>
    //         `;
    //     });
        
    //     container.innerHTML = html;
    // }

    
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
                                    <button onclick="useAsContext(${index})">📎 Utiliser</button>
                                    <button onclick="exportStepText(${index})">💾 Exporter</button>
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
            
            // ========== AJOUTER ICI ==========
            // Vérifier si toutes les étapes sont terminées
            const allStepsDone = workflow.steps.length > 0 && 
                workflow.steps.every(s => s.status === 'success' || s.status === 'error');
            
            if (allStepsDone) {
                const allSuccess = workflow.steps.every(s => s.status === 'success');
                if (allSuccess) {
                    await autoSaveAfterExecution();
                }
            }
            // ========== FIN AJOUT ==========
            
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

            // === AJOUT : Sauvegarde automatique ===
        const allSuccess = workflow.steps.every(s => s.status === 'success');
        if (allSuccess && workflow.steps.length > 0) {
            await autoSaveAfterExecution();
        }

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

    // ========== INITIALISATION ==========
    document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('addStepBtn')?.addEventListener('click', addStep);
    document.getElementById('executeAllBtn')?.addEventListener('click', executeAllSteps);
    document.getElementById('loadDocBtn')?.addEventListener('click', loadDocument);
    document.getElementById('initBtn')?.addEventListener('click', initAssistant);
    document.getElementById('gestionnaireFluxBtn')?.addEventListener('click', openGestionnaireFlux);
    document.getElementById('showConfigBtn')?.addEventListener('click', showConfigModal);
    document.getElementById('quitBtn')?.addEventListener('click', quitApp);
    
    loadPaths();
    loadProvidersWithKeys();
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

    // document.getElementById('showConfigBtn')?.addEventListener('click', showConfigModal);

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

    // ========== FONCTIONS D'EXPORT ET D'IMPORT ==========

    // 1. Exporter une étape individuelle en TXT
    async function exportStepText(stepIndex) {
        const step = workflow.steps[stepIndex];
        if (!step) {
            showNotification('❌ Étape introuvable', 'error');
            return;
        }
        
        let content = [];
        content.push('='.repeat(60));
        content.push(`📌 ${step.name}`);
        content.push('='.repeat(60));
        content.push(`📅 Date: ${new Date().toLocaleString()}`);
        content.push(`📁 Dossier: ${workflow.name}`);
        content.push(`📌 Type: ${step.type}`);
        content.push(`📌 Statut: ${step.status === 'success' ? '✅ Réussi' : step.status === 'error' ? '❌ Échoué' : '⏳ En attente'}`);
        content.push('');
        
        if (step.config && Object.keys(step.config).length > 0) {
            const hasValues = Object.values(step.config).some(v => v);
            if (hasValues) {
                content.push('─'.repeat(40));
                content.push('⚙️ Configuration');
                content.push('─'.repeat(40));
                Object.entries(step.config).forEach(([key, val]) => {
                    if (val) content.push(`${key}: ${val}`);
                });
                content.push('');
            }
        }
        
        if (step.result) {
            content.push('─'.repeat(40));
            content.push('📄 Résultat');
            content.push('─'.repeat(40));
            content.push(step.result);
            content.push('');
        }
        
        if (step.error) {
            content.push('─'.repeat(40));
            content.push('❌ Erreur');
            content.push('─'.repeat(40));
            content.push(step.error);
        }
        
        const blob = new Blob([content.join('\n')], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${step.name.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        showNotification(`💾 Étape "${step.name}" exportée`);
    }



    // 5. Sauvegarder le résultat d'une étape (alias)
    const saveStepResult = exportStepText;

    // 6. Mettre à jour renderWorkflow pour ajouter le bouton d'export sur chaque étape
    // (Remplace la fonction renderWorkflow existante par celle-ci)


    // ========== GESTION DES FLUX ET RAPPORTS ==========

    let fluxActuel = null;

    // Sauvegarder le flux actuel
    async function sauvegarderFlux() {
        const nomFlux = prompt("Nom du flux :", workflow.name || "Mon flux");
        if (!nomFlux) return;
        
        const fluxData = {
            nom: nomFlux,
            workflow: {
                name: workflow.name,
                document: workflow.document,
                steps: workflow.steps.map(step => ({
                    type: step.type,
                    name: step.name,
                    config: step.config,
                    result: step.result,
                    status: step.status
                }))
            }
        };
        
        showNotification('💾 Sauvegarde du flux en cours...', 'info');
        
        try {
            const response = await fetch('/api/flux/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nom: nomFlux,
                    workflow: fluxData,
                    document: workflow.document,
                    steps: workflow.steps
                })
            });
            const result = await response.json();
            
            if (result.success) {
                showNotification(`✅ ${result.message}`);
                chargerListeFlux(); // Rafraîchir la liste
            } else {
                showNotification(`❌ Erreur: ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Sauvegarder un rapport
    async function sauvegarderRapport(contenu, type = 'complet') {
        let nomRapport = prompt("Nom du rapport :", `rapport_${new Date().toLocaleString()}`);
        if (!nomRapport) return;
        
        showNotification('📄 Sauvegarde du rapport...', 'info');
        
        try {
            const response = await fetch('/api/rapports/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nom: nomRapport,
                    contenu: contenu
                })
            });
            const result = await response.json();
            
            if (result.success) {
                showNotification(`✅ Rapport sauvegardé: ${result.nom_fichier}`);
                if (confirm('Voir le rapport ?')) {
                    window.open(`/api/rapports/download/${result.nom_fichier}`, '_blank');
                }
            } else {
                showNotification(`❌ Erreur: ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Charger la liste des flux sauvegardés
    async function chargerListeFlux() {
        try {
            const response = await fetch('/api/flux/list');
            const fluxList = await response.json();
            
            const select = document.getElementById('fluxListe');
            if (!select) return;
            
            select.innerHTML = '<option value="">-- Sélectionner un flux --</option>';
            
            fluxList.forEach(flux => {
                const date = new Date(flux.date_creation).toLocaleString();
                const taille = (flux.taille / 1024).toFixed(1);
                const option = document.createElement('option');
                option.value = flux.nom_fichier;
                option.textContent = `${flux.nom} (${date}) - ${taille} KB`;
                select.appendChild(option);
            });
        } catch(e) {
            console.error('Erreur chargement flux:', e);
        }
    }

    // Charger un flux sélectionné
    async function chargerFlux() {
        const select = document.getElementById('fluxListe');
        const nomFichier = select?.value;
        
        if (!nomFichier) {
            showNotification('❌ Sélectionnez un flux', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/flux/load/${nomFichier}`);
            const result = await response.json();
            
            if (result.success) {
                const data = result.data;
                workflow.name = data.nom;
                workflow.document = data.document || '';
                workflow.steps = data.steps.map(step => ({
                    ...step,
                    id: Date.now() + Math.random(),
                    status: 'pending'
                }));
                
                // Mettre à jour l'UI
                const dossierNameSpan = document.getElementById('dossier_name');
                if (dossierNameSpan) dossierNameSpan.textContent = data.nom;
                
                const textarea = document.getElementById('direct_text');
                if (textarea && data.document) textarea.value = data.document;
                
                renderWorkflow();
                showNotification(`✅ Flux "${data.nom}" chargé (${workflow.steps.length} étapes)`);
            } else {
                showNotification(`❌ ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Supprimer un flux
    async function supprimerFlux() {
        const select = document.getElementById('fluxListe');
        const nomFichier = select?.value;
        
        if (!nomFichier) {
            showNotification('❌ Sélectionnez un flux', 'error');
            return;
        }
        
        if (!confirm('Supprimer définitivement ce flux ?')) return;
        
        try {
            const response = await fetch(`/api/flux/delete/${nomFichier}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                showNotification('✅ Flux supprimé');
                chargerListeFlux();
            } else {
                showNotification(`❌ ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Ouvrir le gestionnaire de flux
    function openGestionnaireFlux() {
        const modalHtml = `
            <div id="fluxManagerModal" class="modal" style="display:block">
                <div class="modal-content" style="width:600px; max-width:90%">
                    <span class="close" onclick="closeModal('fluxManagerModal')">&times;</span>
                    <h3>📁 Gestionnaire de flux</h3>
                    <hr>
                    
                    <h4>📌 Flux sauvegardés</h4>
                    <select id="fluxListe" style="width:100%; margin-bottom:10px">
                        <option value="">Chargement...</option>
                    </select>
                    
                    <div style="display:flex; gap:10px; margin-bottom:20px">
                        <button onclick="chargerFlux()" class="success">📂 Charger</button>
                        <button onclick="supprimerFlux()" class="danger">🗑️ Supprimer</button>
                    </div>
                    
                    <hr>
                    <h4>📂 Dossiers</h4>
                    <div style="display:flex; gap:10px">
                        <button onclick="ouvrirDossierFlux()">📁 Ouvrir dossier flux</button>
                        <button onclick="ouvrirDossierRapports()">📁 Ouvrir dossier rapports</button>
                    </div>
                </div>
            </div>
        `;
        
        if (!document.getElementById('fluxManagerModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        } else {
            document.getElementById('fluxManagerModal').style.display = 'block';
        }
        
        chargerListeFlux();
    }

    // Sauvegarder le rapport complet actuel
    async function sauvegarderRapportComplet() {
        if (workflow.steps.length === 0 && !workflow.document) {
            showNotification('❌ Rien à sauvegarder', 'error');
            return;
        }
        
        let report = [];
        report.push('='.repeat(80));
        report.push('📋 RAPPORT COMPLET DU WORKFLOW JURIDIQUE');
        report.push('='.repeat(80));
        report.push(`📅 Date: ${new Date().toLocaleString()}`);
        report.push(`📁 Dossier: ${workflow.name}`);
        report.push(`📄 Document source: ${document.getElementById('dossier_name')?.textContent || 'Non chargé'}`);
        report.push('');
        report.push('─'.repeat(80));
        report.push('📄 DOCUMENT SOURCE');
        report.push('─'.repeat(80));
        report.push(workflow.document || 'Aucun document chargé');
        report.push('');
        
        workflow.steps.forEach((step, idx) => {
            report.push('─'.repeat(80));
            report.push(`[${idx + 1}] ${step.name} (${step.status === 'success' ? '✅ RÉUSSI' : step.status === 'error' ? '❌ ÉCHOUÉ' : '⏳ EN ATTENTE'})`);
            report.push('─'.repeat(80));
            if (step.result) report.push(step.result);
            if (step.error) report.push(`\n❌ Erreur: ${step.error}`);
            report.push('');
        });
        
        await sauvegarderRapport(report.join('\n'), 'complet');
    }



    // ========== SAUVEGARDE AUTOMATIQUE ==========

    let autoSaveEnabled = true;
    let dernierFluxExecute = null;

    // Sauvegarde automatique après exécution réussie
    async function autoSaveAfterExecution() {
        if (!autoSaveEnabled) return;
        
        const stepsReussies = workflow.steps.filter(s => s.status === 'success').length;
        const totalSteps = workflow.steps.length;
        
        // Sauvegarder seulement si toutes les étapes sont réussies
        if (totalSteps > 0 && stepsReussies === totalSteps) {
            const nomFlux = workflow.name || `flux_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`;
            
            // Générer le rapport
            const rapport = genererRapportTexte();
            
            showNotification('🔄 Sauvegarde automatique du flux...', 'info');
            
            try {
                const response = await fetch('/api/flux/auto_save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nom: nomFlux,
                        workflow: workflow,
                        document: workflow.document,
                        steps: workflow.steps,
                        rapport_contenu: rapport,
                        date_execution: new Date().toISOString()
                    })
                });
                const result = await response.json();
                
                if (result.success) {
                    dernierFluxExecute = result.nom_fichier;
                    showNotification(`✅ Flux "${nomFlux}" sauvegardé automatiquement`);
                    
                    // Afficher une notification avec lien
                    const voirRapport = confirm(`Flux sauvegardé !\nVoir le rapport maintenant ?`);
                    if (voirRapport && result.rapport) {
                        afficherRapportDansUI(result.rapport, nomFlux);
                    }
                }
            } catch(e) {
                console.error('Erreur sauvegarde auto:', e);
            }
        }
    }

    // Générer le rapport en texte
    function genererRapportTexte() {
        let report = [];
        report.push('='.repeat(80));
        report.push('📋 RAPPORT COMPLET DU WORKFLOW JURIDIQUE');
        report.push('='.repeat(80));
        report.push(`📅 Date: ${new Date().toLocaleString()}`);
        report.push(`📁 Dossier: ${workflow.name}`);
        report.push(`📄 Document source: ${document.getElementById('dossier_name')?.textContent || 'Non chargé'}`);
        report.push('');
        report.push('─'.repeat(80));
        report.push('📄 DOCUMENT SOURCE');
        report.push('─'.repeat(80));
        report.push(workflow.document || 'Aucun document chargé');
        report.push('');
        
        workflow.steps.forEach((step, idx) => {
            report.push('─'.repeat(80));
            const statusIcon = step.status === 'success' ? '✅ RÉUSSI' : step.status === 'error' ? '❌ ÉCHOUÉ' : '⏳ EN ATTENTE';
            report.push(`[${idx + 1}] ${step.name} (${statusIcon})`);
            report.push('─'.repeat(80));
            if (step.result) report.push(step.result);
            if (step.error) report.push(`\n❌ Erreur: ${step.error}`);
            report.push('');
        });
        
        return report.join('\n');
    }

    // Afficher le rapport dans l'UI
    function afficherRapportDansUI(rapportNom, fluxNom) {
        // Créer ou récupérer la section rapport
        let rapportSection = document.getElementById('rapportSection');
        if (!rapportSection) {
            const workflowContainer = document.querySelector('.workflow-container');
            rapportSection = document.createElement('div');
            rapportSection.id = 'rapportSection';
            rapportSection.className = 'rapport-section';
            rapportSection.style.cssText = `
                margin-top: 20px;
                border-top: 2px solid #2a5298;
                padding-top: 15px;
            `;
            workflowContainer?.appendChild(rapportSection);
        }
        
        rapportSection.innerHTML = `
            <div class="rapport-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
                <h3>📄 Rapport du flux: ${fluxNom}</h3>
                <div>
                    <button onclick="telechargerRapport('${rapportNom}')" class="success">💾 Télécharger</button>
                    <button onclick="fermerRapport()" class="danger">✖ Fermer</button>
                </div>
            </div>
            <div class="rapport-content" style="
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                max-height: 400px;
                overflow: auto;
                font-family: monospace;
                white-space: pre-wrap;
                border-left: 4px solid #28a745;
            ">
                Chargement du rapport...
            </div>
        `;
        
        // Charger le contenu du rapport
        fetch(`/api/rapports/view/${rapportNom}`)
            .then(res => res.json())
            .then(data => {
                const contentDiv = rapportSection.querySelector('.rapport-content');
                if (contentDiv) {
                    contentDiv.innerHTML = escapeHtml(data.contenu || 'Aucun contenu');
                }
            })
            .catch(err => {
                const contentDiv = rapportSection.querySelector('.rapport-content');
                if (contentDiv) {
                    contentDiv.innerHTML = '<div class="error">❌ Erreur chargement du rapport</div>';
                }
            });
    }

    function fermerRapport() {
        const rapportSection = document.getElementById('rapportSection');
        if (rapportSection) rapportSection.remove();
    }

    async function telechargerRapport(rapportNom) {
        window.open(`/api/rapports/download/${rapportNom}`, '_blank');
    }


    // Améliorer le gestionnaire de flux avec affichage du rapport
    async function chargerFluxAvecRapport() {
        const select = document.getElementById('fluxListe');
        const nomFichier = select?.value;
        
        if (!nomFichier) {
            showNotification('❌ Sélectionnez un flux', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/flux/load/${nomFichier}`);
            const result = await response.json();
            
            if (result.success) {
                const data = result.data;
                workflow.name = data.nom;
                workflow.document = data.document || '';
                workflow.steps = data.steps.map(step => ({
                    ...step,
                    id: Date.now() + Math.random(),
                    status: 'pending'  // Reset status
                }));
                
                // Mettre à jour l'UI
                const dossierNameSpan = document.getElementById('dossier_name');
                if (dossierNameSpan) dossierNameSpan.textContent = data.nom;
                
                const textarea = document.getElementById('direct_text');
                if (textarea && data.document) textarea.value = data.document;
                
                renderWorkflow();
                showNotification(`✅ Flux "${data.nom}" chargé (${workflow.steps.length} étapes)`);
                
                // Vérifier si le flux a un rapport associé
                const rapportCheck = await fetch(`/api/flux/check_rapport/${nomFichier}`);
                const rapportData = await rapportCheck.json();
                
                if (rapportData.success && rapportData.a_rapport) {
                    showNotification(`📄 Ce flux a un rapport associé. Ouvrir ?`, 'info');
                    const openRapport = confirm(`Le flux "${data.nom}" a été exécuté avec succès.\nVoir le rapport associé ?`);
                    if (openRapport) {
                        afficherRapportDansUI(rapportData.rapport_nom, data.nom);
                    }
                }
                
                closeModal('fluxManagerModal');
            } else {
                showNotification(`❌ ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Sauvegarder un flux non exécuté
    async function sauvegarderFluxNonExecute() {
        const nomFlux = prompt("Nom du flux (non exécuté) :", workflow.name || "Mon flux");
        if (!nomFlux) return;
        
        const fluxData = {
            nom: nomFlux,
            date_creation: new Date().toISOString(),
            statut: "non_execute",
            workflow: {
                name: workflow.name,
                document: workflow.document,
                steps: workflow.steps.map(step => ({
                    type: step.type,
                    name: step.name,
                    config: step.config,
                    status: step.status
                }))
            }
        };
        
        try {
            const response = await fetch('/api/flux/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nom: nomFlux,
                    workflow: fluxData,
                    document: workflow.document,
                    steps: workflow.steps
                })
            });
            const result = await response.json();
            
            if (result.success) {
                showNotification(`✅ Flux "${nomFlux}" sauvegardé`);
                chargerListeFlux();
            } else {
                showNotification(`❌ Erreur: ${result.error}`, 'error');
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }

    // Mettre à jour le gestionnaire de flux
    function openGestionnaireFlux() {
        const modalHtml = `
            <div id="fluxManagerModal" class="modal" style="display:block">
                <div class="modal-content" style="width:700px; max-width:90%; max-height:80%; overflow-y:auto">
                    <span class="close" onclick="closeModal('fluxManagerModal')">&times;</span>
                    <h3>📁 Gestionnaire de flux</h3>
                    <hr>
                    
                    <h4>📌 Flux sauvegardés</h4>
                    <select id="fluxListe" style="width:100%; margin-bottom:10px">
                        <option value="">Chargement...</option>
                    </select>
                    
                    <div style="display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap">
                        <button onclick="chargerFluxAvecRapport()" class="success">📂 Charger le flux</button>
                        <button onclick="supprimerFlux()" class="danger">🗑️ Supprimer</button>
                    </div>
                    
                    
                    <hr>
                    <div id="fluxRapportPreview" style="display:none; margin-top:15px">
                        <h4>📄 Rapport associé</h4>
                        <div id="fluxRapportContent" style="
                            background:#f8f9fa;
                            padding:10px;
                            border-radius:5px;
                            max-height:300px;
                            overflow:auto;
                            font-family:monospace;
                            font-size:12px;
                            white-space:pre-wrap
                        "></div>
                    </div>
                    
                </div>
            </div>
        `;
        
        if (!document.getElementById('fluxManagerModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        } else {
            document.getElementById('fluxManagerModal').style.display = 'block';
        }
        
        chargerListeFlux();
        
        // Ajouter l'événement pour prévisualiser le rapport
        const fluxSelect = document.getElementById('fluxListe');
        if (fluxSelect) {
            fluxSelect.onchange = async function() {
                const nomFichier = this.value;
                if (nomFichier) {
                    const response = await fetch(`/api/flux/check_rapport/${nomFichier}`);
                    const data = await response.json();
                    const previewDiv = document.getElementById('fluxRapportPreview');
                    const contentDiv = document.getElementById('fluxRapportContent');
                    
                    if (data.success && data.a_rapport) {
                        previewDiv.style.display = 'block';
                        contentDiv.innerHTML = data.contenu.substring(0, 1000) + '...';
                    } else {
                        previewDiv.style.display = 'none';
                    }
                }
            };
        }
    }

    async function sauvegarderRapportManuel() {
        if (workflow.steps.length === 0 && !workflow.document) {
            showNotification('❌ Rien à sauvegarder', 'error');
            return;
        }
        const rapport = genererRapportTexte();
        const nomRapport = prompt("Nom du rapport :", `rapport_${workflow.name || 'flux'}`);
        if (!nomRapport) return;
        
        try {
            const response = await fetch('/api/rapports/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nom: nomRapport,
                    contenu: rapport
                })
            });
            const result = await response.json();
            if (result.success) {
                showNotification(`✅ Rapport "${nomRapport}" sauvegardé`);
            }
        } catch(e) {
            showNotification(`❌ Erreur: ${e.message}`, 'error');
        }
    }
    // Ajouter les routes pour ouvrir les dossiers (backend)
    // À ajouter dans app.py:
    /*
    @app.route('/api/flux/dossier', methods=['GET'])
    def open_flux_folder():
        import subprocess
        import platform
        chemin = os.path.abspath(FLUX_DIR)
        if platform.system() == 'Windows':
            os.startfile(chemin)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', chemin])
        else:  # Linux
            subprocess.run(['xdg-open', chemin])
        return jsonify({'success': True})
    */
    // document.getElementById('gestionnaireFluxBtn')?.addEventListener('click', openGestionnaireFlux);

    // Charger les chemins des dossiers
async function loadPaths() {
    // Afficher des chemins par défaut
    const fluxPathEl = document.getElementById('fluxPath');
    const rapportsPathEl = document.getElementById('rapportsPath');
    
    if (fluxPathEl) fluxPathEl.innerText = './flux/';
    if (rapportsPathEl) rapportsPathEl.innerText = './rapports/';
    
    // Essayer de charger depuis l'API si disponible
    try {
        const response = await fetch('/api/paths');
        if (response.ok) {
            const data = await response.json();
            if (fluxPathEl) fluxPathEl.innerText = data.flux || './flux/';
            if (rapportsPathEl) rapportsPathEl.innerText = data.rapports || './rapports/';
        }
    } catch(e) {
        console.log('API paths non disponible, utilisation des chemins par défaut');
    }
}


// Fonction pour quitter l'application
async function quitApp() {
    if (confirm('Êtes-vous sûr de vouloir quitter ?')) {
        try {
            await fetch('/api/shutdown', { method: 'POST' });
        } catch(e) {
            console.log('Shutdown error:', e);
        }
        setTimeout(function() { window.close(); }, 500);
    }
}