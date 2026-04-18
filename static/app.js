// Variables globales
let state = {
  text: "",
  lastResult: "",
  currentText: ""
};

// Fonction API unifiée
async function api(url, data, method = "POST") {
  const options = {
    method,
    headers: { "Content-Type": "application/json" }
  };
  if (data && method !== "GET") {
    options.body = JSON.stringify(data);
  }
  const res = await fetch(url, options);
  return res.json();
}

function setLoading(id) {
  const element = document.getElementById(id);
  if (element) element.innerHTML = '<div class="loading">Chargement...</div>';
}

function setResult(id, text) {
  const element = document.getElementById(id);
  if (element) element.innerHTML = '<div class="result-box">' + (text || "").replace(/\n/g, '<br>') + '</div>';
}

// Fonction pour changer d'onglet (améliorée)
function showTab(tabName, element) {
  var contents = document.getElementsByClassName('tab-content');
  for (var i = 0; i < contents.length; i++) {
    contents[i].classList.remove('active');
  }
  var tabs = document.getElementsByClassName('tab');
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].classList.remove('active');
  }
  document.getElementById(tabName).classList.add('active');
  if (element) {
    element.classList.add('active');
  }
  
  // Refresh data when opening config tab
  if (tabName === 'config') {
    loadProviders();
    loadAllProvidersForConfig();
  }
}

// Initialisation des onglets avec dataset
document.querySelectorAll(".tab").forEach(btn => {
  btn.onclick = () => {
    const currentActive = document.querySelector(".tab.active");
    if (currentActive) currentActive.classList.remove("active");
    btn.classList.add("active");

    const currentContent = document.querySelector(".tab-content.active");
    if (currentContent) currentContent.classList.remove("active");
    const tabId = btn.getAttribute('data-tab') || btn.innerText.toLowerCase().replace(/[^a-z]/g, '');
    document.getElementById(tabId).classList.add("active");
  };
});

// Load providers that have API keys configured (for sidebar)
async function loadProvidersWithKeys() {
  try {
    const data = await api("/api/providers/with_keys", {}, "GET");
    const select = document.getElementById('provider_select');
    if (!select) return;
    select.innerHTML = '<option value="">-- Selectionner un provider --</option>';
    
    const modelSelect = document.getElementById('model_select');

    if (data.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.disabled = true;
      opt.textContent = "Aucun provider avec API key - Configurez vos clés dans l'onglet Configuration";
      select.appendChild(opt);

      if (modelSelect) {
        modelSelect.innerHTML = '<option value="">-- Selectionnez d\'abord un provider --</option>';
        modelSelect.disabled = true;
      }
    } else {
      for (const provider of data) {
        const option = document.createElement('option');
        option.value = provider.name;
        const modelText = provider.models_count === 1 ? 'modele' : 'modeles';
        option.textContent = `${provider.name} (${provider.models_count} ${modelText})`;
        select.appendChild(option);
      }
      if (modelSelect) {
        modelSelect.innerHTML = '<option value="">-- Selectionnez d\'abord un provider --</option>';
        modelSelect.disabled = true;
      }
    }
  } catch(e) {
    console.error('Error loading providers:', e);
    const select = document.getElementById('provider_select');
    if (select) select.innerHTML = '<option value="">Erreur de chargement</option>';
  }
}

// Load models for selected provider
async function loadModelsForProviderSelect() {
  var providerName = document.getElementById('provider_select').value;
  var modelSelect = document.getElementById('model_select');
  
  if (!modelSelect) return;
  
  if (!providerName) {
    modelSelect.innerHTML = '<option value="">-- Selectionnez d\'abord un provider --</option>';
    modelSelect.disabled = true;
    return;
  }
  
  modelSelect.innerHTML = '<option value="">Chargement des modeles...</option>';
  modelSelect.disabled = true;
  
  try {
    var data = await api('/api/models/available/' + encodeURIComponent(providerName), {}, "GET");
    
    if (data.length === 0) {
      modelSelect.innerHTML = '<option value="">Aucun modele disponible pour ce provider</option>';
      modelSelect.disabled = true;
    } else {
      modelSelect.innerHTML = '<option value="">-- Selectionner un modele --</option>';
      for (var model of data) {
        var option = document.createElement('option');
        option.value = model.model_key;
        option.textContent = model.display_name + ' (' + model.context_length + ' tokens)';
        modelSelect.appendChild(option);
      }
      modelSelect.disabled = false;
    }
  } catch(e) {
    console.error('Error loading models:', e);
    modelSelect.innerHTML = '<option value="">Erreur de chargement</option>';
    modelSelect.disabled = true;
  }
}

// Initialize assistant
async function initAssistant() {
  var providerName = document.getElementById('provider_select').value;
  var modelKey = document.getElementById('model_select').value;
  var temperature = parseFloat(document.getElementById('temperature').value);
  var maxTokens = parseInt(document.getElementById('max_tokens').value);
  
  if (!providerName) {
    alert('Veuillez d\'abord selectionner un provider');
    return;
  }
  
  if (!modelKey) {
    alert('Veuillez selectionner un modele');
    return;
  }
  
  var statusDiv = document.getElementById('init_status');
  statusDiv.innerHTML = '<div class="loading">Initialisation...</div>';
  
  try {
    var result = await api('/api/init', {
      provider_name: providerName,
      model_key: modelKey,
      temperature: temperature,
      max_tokens: maxTokens
    });
    if (result.success) {
      statusDiv.innerHTML = '<div class="success-msg">✅ Assistant initialise avec ' + result.model_display + '</div>';
    } else {
      statusDiv.innerHTML = '<div class="error">❌ ' + result.error + '</div>';
    }
  } catch(e) {
    statusDiv.innerHTML = '<div class="error">❌ ' + e.message + '</div>';
  }
}

// Load all providers for config tab dropdown
async function loadAllProvidersForConfig() {
  try {
    var data = await api('/api/providers/list', {}, "GET");
    var select = document.getElementById('model_provider_select');
    if (select) {
      select.innerHTML = '<option value="">-- Choisir un provider --</option>';
      for (var provider of data) {
        var option = document.createElement('option');
        option.value = provider.name;
        option.textContent = provider.name;
        select.appendChild(option);
      }
    }
  } catch(e) {
    console.error('Error loading providers for config:', e);
  }
}

// Load providers for management table
async function loadProvidersTable() {
  try {
    var data = await api('/api/providers/list', {}, "GET");
    var tbody = document.getElementById('providers_table_body');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    for (var provider of data) {
      var row = tbody.insertRow();
      row.insertCell(0).textContent = provider.name;
      row.insertCell(1).textContent = provider.url;
      
      var apiKeyCell = row.insertCell(2);
      var maskedKey = provider.api_key ? '•' + provider.api_key.slice(-8) : 'Non configuree';
      apiKeyCell.innerHTML = '<span class="api-key-masked">' + maskedKey + '</span>';
      
      var actionsCell = row.insertCell(3);
      actionsCell.innerHTML = '<button onclick="editApiKey(\'' + provider.name + '\')" style="margin:2px">✏️ Cle</button>' +
        '<button onclick="deleteProvider(\'' + provider.name + '\')" class="danger" style="margin:2px">🗑️</button>';
    }
  } catch(e) {
    console.error('Error loading providers:', e);
  }
}

// Load models for a provider in config tab
async function loadModelsForProvider(providerName) {
  try {
    var data = await api('/api/models/list/' + providerName, {}, "GET");
    var container = document.getElementById('models_list');
    if (!container) return;
    
    if (data.length === 0) {
      container.innerHTML = '<p>Aucun modele pour ce provider</p>';
    } else {
      var html = '<table><thead><tr><th>Cle modele</th><th>Nom affiche</th><th>Contexte</th><th>Action</th></tr></thead><tbody>';
      for (var model of data) {
        html += '<tr>' +
          '<td>' + model.model_key + '</td>' +
          '<td>' + model.display_name + '</td>' +
          '<td>' + model.context_length + '</td>' +
          '<td><button onclick="deleteModel(\'' + model.model_key + '\')" class="danger">🗑️</button></td>' +
          '</tr>';
      }
      html += '</tbody></table>';
      container.innerHTML = html;
    }
  } catch(e) {
    console.error('Error loading models:', e);
  }
}

// Show add provider modal
function showAddProviderModal() {
  const nameInput = document.getElementById('provider_name');
  const urlInput = document.getElementById('provider_url');
  const keyInput = document.getElementById('provider_api_key');
  if (nameInput) nameInput.value = '';
  if (urlInput) urlInput.value = '';
  if (keyInput) keyInput.value = '';
  const modal = document.getElementById('addProviderModal');
  if (modal) modal.style.display = 'block';
}

// Close modal
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'none';
}

// Add provider
async function addProvider() {
  var name = document.getElementById('provider_name').value.trim();
  var url = document.getElementById('provider_url').value.trim();
  var apiKey = document.getElementById('provider_api_key').value;
  
  if (!name || !url) {
    alert('Nom et URL sont requis');
    return;
  }
  
  try {
    var result = await api('/api/providers/add', { name: name, url: url, api_key: apiKey });
    if (result.success) {
      alert(result.message);
      closeModal('addProviderModal');
      loadProvidersTable();
      loadProvidersWithKeys();
      loadAllProvidersForConfig();
    } else {
      alert('Erreur: ' + result.message);
    }
  } catch(e) {
    alert('Erreur: ' + e.message);
  }
}

// Edit API key
async function editApiKey(providerName) {
  var newKey = prompt('Entrez la nouvelle API key pour ' + providerName + ':');
  if (newKey !== null) {
    try {
      var result = await api('/api/providers/update_api_key', { name: providerName, api_key: newKey });
      if (result.success) {
        alert(result.message);
        loadProvidersTable();
        loadProvidersWithKeys();
      } else {
        alert('Erreur: ' + result.message);
      }
    } catch(e) {
      alert('Erreur: ' + e.message);
    }
  }
}

// Delete provider
async function deleteProvider(providerName) {
  if (confirm('Supprimer ' + providerName + ' et tous ses modeles ?')) {
    try {
      var result = await api('/api/providers/delete', { name: providerName }, "DELETE");
      if (result.success) {
        alert(result.message);
        loadProvidersTable();
        loadProvidersWithKeys();
        loadAllProvidersForConfig();
        var modelsList = document.getElementById('models_list');
        if (modelsList) modelsList.innerHTML = '';
        var providerSelect = document.getElementById('provider_select');
        if (providerSelect) {
          providerSelect.innerHTML = '<option value="">-- Selectionner un provider --</option>';
        }
        var modelSelect = document.getElementById('model_select');
        if (modelSelect) {
          modelSelect.innerHTML = '<option value="">-- Selectionnez d\'abord un provider --</option>';
          modelSelect.disabled = true;
        }
      } else {
        alert('Erreur: ' + result.message);
      }
    } catch(e) {
      alert('Erreur: ' + e.message);
    }
  }
}

// Show add model modal
function showAddModelModal() {
  loadProviderSelectForModel();
  const keyInput = document.getElementById('model_key');
  const nameInput = document.getElementById('model_display_name');
  const contextInput = document.getElementById('model_context');
  if (keyInput) keyInput.value = '';
  if (nameInput) nameInput.value = '';
  if (contextInput) contextInput.value = '';
  const modal = document.getElementById('addModelModal');
  if (modal) modal.style.display = 'block';
}

// Load providers for select dropdown in add model modal
async function loadProviderSelectForModel() {
  try {
    var data = await api('/api/providers/list', {}, "GET");
    var select = document.getElementById('model_provider');
    if (!select) return;
    select.innerHTML = '<option value="">-- Selectionner un provider --</option>';
    for (var provider of data) {
      var option = document.createElement('option');
      option.value = provider.name;
      option.textContent = provider.name;
      select.appendChild(option);
    }
  } catch(e) {
    console.error('Error loading providers:', e);
  }
}

// Add model
async function addModel() {
  var providerName = document.getElementById('model_provider').value;
  var modelKey = document.getElementById('model_key').value.trim();
  var displayName = document.getElementById('model_display_name').value.trim();
  var contextLength = parseInt(document.getElementById('model_context').value);
  
  if (!providerName || !modelKey || !displayName || !contextLength) {
    alert('Tous les champs sont requis');
    return;
  }
  
  try {
    var result = await api('/api/models/add', {
      provider_name: providerName,
      model_key: modelKey,
      display_name: displayName,
      context_length: contextLength
    });
    if (result.success) {
      alert(result.message);
      closeModal('addModelModal');
      loadModelsForProvider(providerName);
      loadProvidersWithKeys();
    } else {
      alert('Erreur: ' + result.message);
    }
  } catch(e) {
    alert('Erreur: ' + e.message);
  }
}

// Delete model
async function deleteModel(modelKey) {
  if (confirm('Supprimer le modele ' + modelKey + ' ?')) {
    try {
      var result = await api('/api/models/delete', { model_key: modelKey }, "DELETE");
      if (result.success) {
        alert(result.message);
        var providerSelect = document.getElementById('model_provider_select');
        if (providerSelect && providerSelect.value) {
          loadModelsForProvider(providerSelect.value);
        }
        loadProvidersWithKeys();
      } else {
        alert('Erreur: ' + result.message);
      }
    } catch(e) {
      alert('Erreur: ' + e.message);
    }
  }
}

// Load document
async function loadDocument() {
  var file = document.getElementById('file_upload').files[0];
  var directText = document.getElementById('direct_text').value;
  
  if (file) {
    var formData = new FormData();
    formData.append('file', file);
    try {
      var response = await fetch('/api/upload', { method: 'POST', body: formData });
      var result = await response.json();
      if (result.success) {
        state.currentText = result.text;
        state.text = result.text;
        document.getElementById('doc_status').innerHTML = '<div class="success-msg">✅ ' + result.filename + ' charge</div>';
        var analyseInfo = document.getElementById('analyse_info');
        if (analyseInfo) analyseInfo.innerHTML = '<div class="info">📄 Document actif: ' + result.filename + '</div>';
      } else {
        document.getElementById('doc_status').innerHTML = '<div class="error">❌ ' + result.error + '</div>';
      }
    } catch(e) {
      document.getElementById('doc_status').innerHTML = '<div class="error">❌ ' + e.message + '</div>';
    }
  } else if (directText) {
    state.currentText = directText;
    state.text = directText;
    document.getElementById('doc_status').innerHTML = '<div class="success-msg">✅ Texte valide</div>';
    var analyseInfo = document.getElementById('analyse_info');
    if (analyseInfo) analyseInfo.innerHTML = '<div class="info">📄 Texte direct (' + state.currentText.length + ' caracteres)</div>';
  } else {
    document.getElementById('doc_status').innerHTML = '<div class="error">❌ Aucun document</div>';
  }
}

// API call wrapper
async function callApi(action) {
  if (!state.currentText && action !== 'recherche' && action !== 'generer_prompt') {
    alert("Veuillez d'abord charger un document");
    return;
  }
  
  var data = { text: state.currentText };
  var resultDiv = 'analyse_result';
  
  switch(action) {
    case 'analyser':
      resultDiv = 'analyse_result';
      break;
    case 'conclusions':
      resultDiv = 'analyse_result';
      break;
    case 'ameliorer':
      resultDiv = 'analyse_result';
      break;
    case 'email':
      resultDiv = 'email_result';
      break;
    case 'rediger':
      data.acte_type = document.getElementById('acte_type').value;
      data.instructions = document.getElementById('instructions').value;
      resultDiv = 'redaction_result';
      break;
    case 'recherche':
      data.query = document.getElementById('search_query').value || state.currentText;
      resultDiv = 'recherche_result';
      break;
    case 'analyse_dossier':
      var files = document.getElementById('dossier_files').files;
      if (files.length === 0) { alert('Selectionnez des fichiers'); return; }
      var formData = new FormData();
      for (var i = 0; i < files.length; i++) formData.append('files', files[i]);
      try {
        var response = await fetch('/api/analyse_dossier', { method: 'POST', body: formData });
        var result = await response.json();
        var dossierResult = document.getElementById('dossier_result');
        if (dossierResult) dossierResult.innerHTML = '<div class="result-box">' + result.result + '</div>';
        state.lastResult = result.result;
        var lastResultElement = document.getElementById('last_result');
        if (lastResultElement) lastResultElement.innerHTML = '<div class="result-box">' + result.result + '</div>';
      } catch(e) {
        var dossierResult = document.getElementById('dossier_result');
        if (dossierResult) dossierResult.innerHTML = '<div class="error">❌ ' + e.message + '</div>';
      }
      return;
    case 'preparer_audience':
      resultDiv = 'audience_result';
      break;
    case 'generer_arguments':
      resultDiv = 'arguments_result';
      break;
    case 'generer_prompt':
      data.prompt_type = document.getElementById('prompt_type').value;
      data.situation = document.getElementById('situation').value;
      if (!data.situation) { alert('Decrivez votre situation'); return; }
      resultDiv = 'prompt_result';
      break;
    case 'appliquer_tampon':
      data.config = {
        avocat: {
          nom: document.getElementById('nom').value,
          prenom: document.getElementById('prenom').value,
          barreau: document.getElementById('barreau').value
        }
      };
      resultDiv = 'tampon_result';
      break;
    default:
      return;
  }
  
  var resultElement = document.getElementById(resultDiv);
  if (resultElement) {
    resultElement.innerHTML = '<div class="loading">Traitement en cours...</div>';
  }
  
  try {
    var result = await api('/api/' + action, data);
    if (result.result) {
      if (resultElement) {
        resultElement.innerHTML = '<div class="result-box">' + result.result.replace(/\n/g, '<br>') + '</div>';
      }
      state.lastResult = result.result;
      var lastResultElement = document.getElementById('last_result');
      if (lastResultElement) {
        lastResultElement.innerHTML = '<div class="result-box">' + result.result.replace(/\n/g, '<br>') + '</div>';
      }
    } else {
      if (resultElement) {
        resultElement.innerHTML = '<div class="error">❌ ' + (result.error || 'Erreur inconnue') + '</div>';
      }
    }
  } catch(e) {
    if (resultElement) {
      resultElement.innerHTML = '<div class="error">❌ ' + e.message + '</div>';
    }
  }
}

function downloadResult() {
  if (state.lastResult) {
    var blob = new Blob([state.lastResult], { type: 'text/plain' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'resultat_' + Date.now() + '.txt';
    a.click();
  } else {
    alert('Aucun resultat a telecharger');
  }
}

function copyResult() {
  if (state.lastResult) {
    navigator.clipboard.writeText(state.lastResult);
    alert('✅ Copie dans le presse-papier');
  }
}

async function quitApp() {
  if (confirm('Etes-vous sur de vouloir quitter ?')) {
    try {
      await fetch('/api/shutdown', { method: 'POST' });
    } catch(e) {}
    setTimeout(function() { window.close(); }, 500);
  }
}

// Écouteurs d'événements pour les boutons principaux
document.addEventListener('DOMContentLoaded', function() {
  // Initialisation des providers
  loadProvidersWithKeys();
  loadProvidersTable();
  loadAllProvidersForConfig();
  
  // Écouteurs pour les sliders
  const tempSlider = document.getElementById('temperature');
  const tempSpan = document.getElementById('temp_value');
  if (tempSlider && tempSpan) {
    tempSlider.oninput = function() { tempSpan.innerText = this.value; };
  }
  
  const tokensSlider = document.getElementById('max_tokens');
  const tokensSpan = document.getElementById('tokens_value');
  if (tokensSlider && tokensSpan) {
    tokensSlider.oninput = function() { tokensSpan.innerText = this.value; };
  }
  
  // Écouteurs pour les providers
  const providerSelect = document.getElementById('provider_select');
  if (providerSelect) {
    providerSelect.onchange = loadModelsForProviderSelect;
  }
  
  const modelProviderSelect = document.getElementById('model_provider_select');
  if (modelProviderSelect) {
    modelProviderSelect.onchange = function() { loadModelsForProvider(this.value); };
  }
  
  // Écouteurs pour les boutons principaux
  const initBtn = document.getElementById('initBtn');
  if (initBtn) initBtn.onclick = initAssistant;
  
  const loadDocBtn = document.getElementById('loadDocBtn');
  if (loadDocBtn) loadDocBtn.onclick = loadDocument;
  
  const quitBtn = document.getElementById('quitBtn');
  if (quitBtn) quitBtn.onclick = quitApp;
  
  // Boutons des onglets d'action
  const analyserBtn = document.getElementById('analyserBtn');
  if (analyserBtn) analyserBtn.onclick = () => callApi('analyser');
  
  const conclusionsBtn = document.getElementById('conclusionsBtn');
  if (conclusionsBtn) conclusionsBtn.onclick = () => callApi('conclusions');
  
  const ameliorerBtn = document.getElementById('ameliorerBtn');
  if (ameliorerBtn) ameliorerBtn.onclick = () => callApi('ameliorer');
  
  const emailBtn = document.getElementById('emailBtn');
  if (emailBtn) emailBtn.onclick = () => callApi('email');
  
  const redigerBtn = document.getElementById('redigerBtn');
  if (redigerBtn) redigerBtn.onclick = () => callApi('rediger');
  
  const rechercheBtn = document.getElementById('rechercheBtn');
  if (rechercheBtn) rechercheBtn.onclick = () => callApi('recherche');
  
  const analyseDossierBtn = document.getElementById('analyseDossierBtn');
  if (analyseDossierBtn) analyseDossierBtn.onclick = () => callApi('analyse_dossier');
  
  const preparerAudienceBtn = document.getElementById('preparerAudienceBtn');
  if (preparerAudienceBtn) preparerAudienceBtn.onclick = () => callApi('preparer_audience');
  
  const genererArgumentsBtn = document.getElementById('genererArgumentsBtn');
  if (genererArgumentsBtn) genererArgumentsBtn.onclick = () => callApi('generer_arguments');
  
  const genererPromptBtn = document.getElementById('genererPromptBtn');
  if (genererPromptBtn) genererPromptBtn.onclick = () => callApi('generer_prompt');
  
  const appliquerTamponBtn = document.getElementById('appliquerTamponBtn');
  if (appliquerTamponBtn) appliquerTamponBtn.onclick = () => callApi('appliquer_tampon');
  
  const addProviderBtn = document.getElementById('addProviderBtn');
  if (addProviderBtn) addProviderBtn.onclick = showAddProviderModal;
  
  const addModelBtn = document.getElementById('addModelBtn');
  if (addModelBtn) addModelBtn.onclick = showAddModelModal;
  
  const downloadResultBtn = document.getElementById('downloadResultBtn');
  if (downloadResultBtn) downloadResultBtn.onclick = downloadResult;
  
  const copyResultBtn = document.getElementById('copyResultBtn');
  if (copyResultBtn) copyResultBtn.onclick = copyResult;
});