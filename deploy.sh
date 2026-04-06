#!/bin/bash
# ============================================
# ASSISTANT JURIDIQUE IA - INSTALLATION
# Version: 3.2 - Avec setup.py
# ============================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo ""
echo "============================================"
echo "   ASSISTANT JURIDIQUE IA - INSTALLATION"
echo "============================================"
echo ""

# ============================================
# 1. VÉRIFICATION DE GOOGLE DRIVE
# ============================================
print_step "Vérification de Google Drive..."

if [ ! -d "/content/drive/MyDrive" ]; then
    echo "❌ Drive non monté. Exécutez d'abord la cellule de montage."
    exit 1
fi
print_success "Drive accessible"

# ============================================
# 2. CRÉATION DU DOSSIER DANS DRIVE
# ============================================
DRIVE_PATH="/content/drive/MyDrive/assistant-juridique"

print_step "Création du dossier dans votre Drive..."
rm -rf "$DRIVE_PATH" 2>/dev/null || true
mkdir -p "$DRIVE_PATH/utils"
mkdir -p "$DRIVE_PATH/config"
mkdir -p "$DRIVE_PATH/data/documents"
mkdir -p "$DRIVE_PATH/data/analyses"
mkdir -p "$DRIVE_PATH/data/actes"

print_success "Dossier créé : assistant-juridique"

# ============================================
# 3. TÉLÉCHARGEMENT DES FICHIERS DEPUIS GITHUB
# ============================================
print_step "Téléchargement des fichiers depuis GitHub..."

cd /tmp
rm -rf temp_repo 2>/dev/null || true
git clone https://github.com/DanielOmola/assistant-juridique.git temp_repo 2>/dev/null

if [ ! -d "/tmp/temp_repo" ]; then
    print_error "Impossible de télécharger le dépôt GitHub."
    exit 1
fi

print_step "Copie des fichiers..."

# Copier les notebooks
cp /tmp/temp_repo/01_backend_llm.ipynb "$DRIVE_PATH/" 2>/dev/null || true
cp /tmp/temp_repo/02_frontend.ipynb "$DRIVE_PATH/" 2>/dev/null || true

# Copier setup.py
cp /tmp/temp_repo/setup.py "$DRIVE_PATH/" 2>/dev/null || true

# Copier les utils
cp -r /tmp/temp_repo/utils/* "$DRIVE_PATH/utils/" 2>/dev/null || true

# Copier les logs
cp -r /tmp/temp_repo/logs/* "$DRIVE_PATH/logs/" 2>/dev/null || true

# Copier la config
cp /tmp/temp_repo/config/*.yaml "$DRIVE_PATH/config/" 2>/dev/null || true

rm -rf /tmp/temp_repo

print_success "Fichiers copiés"

# ============================================
# 4. INSTALLATION DES DÉPENDANCES
# ============================================
print_step "Installation des dépendances Python..."
pip install -q openai PyPDF2 python-docx ipywidgets anthropic groq pyyaml reportlab
print_success "Dépendances installées"

# ============================================
# 5. INSTALLATION DU PACKAGE EN MODE DEV
# ============================================
print_step "Installation du package en mode développement..."
cd "$DRIVE_PATH"
pip install -q -e . 2>/dev/null || echo "⚠️ pip install -e . ignoré"
print_success "Package installé"

# ============================================
# 6. CRÉATION DES FICHIERS DE CONFIGURATION
# ============================================
print_step "Création des fichiers de configuration..."

cat > "$DRIVE_PATH/config/api_keys.yaml" << 'EOF'
api_keys:
  groq: "VOTRE_CLE_GROQ_ICI"
  openai: ""
  anthropic: ""
default_model: "llama-3.3-70b-versatile"
EOF

cat > "$DRIVE_PATH/config/tampon_config.yaml" << 'EOF'
avocat:
  nom: "VOTRE_NOM"
  prenom: "VOTRE_PRENOM"
  fonction: "Avocat"
  barreau: "VOTRE_BARREAU"
  siret: "VOTRE_SIRET"
  telephone: "VOTRE_TELEPHONE"
  email: "VOTRE_EMAIL"
  adresse: "VOTRE_ADRESSE"
options:
  type_tampon: "officiel"
  position: "debut"
  date_format: "%d/%m/%Y"
EOF

print_success "Configuration créée"

# ============================================
# 7. RÉCAPITULATIF
# ============================================
echo ""
echo "============================================"
print_success "INSTALLATION TERMINÉE !"
echo "============================================"
echo ""
echo "📁 DOSSIER : $DRIVE_PATH"
echo ""
ls -la "$DRIVE_PATH/"
echo ""
echo "🚀 Lancez 01_backend_llm.ipynb puis 02_frontend.ipynb"
echo "============================================"