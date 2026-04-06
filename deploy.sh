#!/bin/bash
# ============================================
# ASSISTANT JURIDIQUE IA - INSTALLATION DANS DRIVE
# Version: 2.0 - Installation persistante
# ============================================

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }

echo ""
echo "============================================"
echo "   ASSISTANT JURIDIQUE IA - INSTALLATION"
echo "============================================"
echo ""

# ============================================
# 1. MONTAGE DE GOOGLE DRIVE
# ============================================
print_step "Montage de Google Drive..."

# Nettoyer l'ancien point de montage
if [ -d "/content/drive" ]; then
    rm -rf /content/drive
fi

# Monter Drive
python3 -c "
from google.colab import drive
drive.mount('/content/drive')
" || {
    print_error "Impossible de monter Google Drive"
    exit 1
}

print_success "Google Drive monté"

# ============================================
# 2. CRÉATION DES DOSSIERS DANS DRIVE
# ============================================
print_step "Création des dossiers dans Drive..."

DRIVE_PATH="/content/drive/MyDrive/assistant-juridique"

# Supprimer l'ancienne installation si elle existe
if [ -d "$DRIVE_PATH" ]; then
    print_warning "Suppression de l'ancienne installation..."
    rm -rf "$DRIVE_PATH"
fi

# Créer la structure
mkdir -p "$DRIVE_PATH"
mkdir -p "$DRIVE_PATH/notebooks"
mkdir -p "$DRIVE_PATH/utils"
mkdir -p "$DRIVE_PATH/config"
mkdir -p "$DRIVE_PATH/data"
mkdir -p "$DRIVE_PATH/data/documents"
mkdir -p "$DRIVE_PATH/data/analyses"
mkdir -p "$DRIVE_PATH/data/actes"

print_success "Dossiers créés dans Drive"

# ============================================
# 3. TÉLÉCHARGEMENT DU DÉPÔT
# ============================================
print_step "Téléchargement des fichiers..."

# Cloner le dépôt dans un dossier temporaire
TEMP_DIR="/content/assistant_temp"
rm -rf "$TEMP_DIR"
git clone https://github.com/DanielOmola/assistant-juridique.git "$TEMP_DIR"

# Copier les fichiers vers Drive
cp -r "$TEMP_DIR/notebooks/"* "$DRIVE_PATH/notebooks/" 2>/dev/null || true
cp -r "$TEMP_DIR/utils/"* "$DRIVE_PATH/utils/" 2>/dev/null || true
cp "$TEMP_DIR/config/"*.yaml "$DRIVE_PATH/config/" 2>/dev/null || true

# Nettoyer
rm -rf "$TEMP_DIR"

print_success "Fichiers installés dans Drive"

# ============================================
# 4. INSTALLATION DES DÉPENDANCES
# ============================================
print_step "Installation des dépendances Python..."

pip install -q openai PyPDF2 python-docx ipywidgets anthropic groq pyyaml reportlab

print_success "Dépendances installées"

# ============================================
# 5. CRÉATION DES FICHIERS DE CONFIGURATION
# ============================================
print_step "Création des fichiers de configuration..."

# Créer api_keys.yaml
cat > "$DRIVE_PATH/config/api_keys.yaml" << 'EOF'
# ============================================
# CONFIGURATION DES CLÉS API - À REMPLIR
# ============================================
# 1. Obtenez une clé gratuite sur https://console.groq.com
# 2. Renseignez-la ci-dessous
# ============================================

api_keys:
  groq: "VOTRE_CLE_GROQ_ICI"
  openai: ""
  anthropic: ""

default_model: "llama-3.3-70b-versatile"
EOF

# Créer tampon_config.yaml
cat > "$DRIVE_PATH/config/tampon_config.yaml" << 'EOF'
# ============================================
# CONFIGURATION DU TAMPON AVOCAT
# ============================================
# À personnaliser avec vos informations

avocat:
  nom: "NOM"
  prenom: "PRENOM"
  fonction: "Avocat"
  barreau: "BARREAU"
  siret: "SIRET"
  telephone: "TELEPHONE"
  email: "EMAIL"
  adresse: "ADRESSE COMPLETE"

options:
  type_tampon: "officiel"
  position: "debut"
  date_format: "%d/%m/%Y"
EOF

print_success "Fichiers de configuration créés"

# ============================================
# 6. CRÉATION DU NOTEBOOK DE LANCEMENT
# ============================================
print_step "Création du lanceur..."

cat > "$DRIVE_PATH/launch.ipynb" << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 🚀 Assistant Juridique IA - Lancement\n",
    "\n",
    "Cliquez sur **Run All** pour démarrer l'assistant"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Vérifier Drive\n",
    "from google.colab import drive\n",
    "import os\n",
    "\n",
    "if not os.path.exists('/content/drive/MyDrive'):\n",
    "    drive.mount('/content/drive')\n",
    "    print(\"✅ Drive monté\")\n",
    "else:\n",
    "    print(\"✅ Drive déjà accessible\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Lancer le backend\n",
    "%run /content/drive/MyDrive/assistant-juridique/notebooks/01_backend_llm.ipynb"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Lancer l'interface\n",
    "%run /content/drive/MyDrive/assistant-juridique/notebooks/02_frontend.ipynb"
   ]
  }
 ],
 "metadata": {
  "colab": {
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
EOF

print_success "Lanceur créé"

# ============================================
# 7. RÉCAPITULATIF FINAL
# ============================================
echo ""
echo "============================================"
print_success "INSTALLATION TERMINÉE AVEC SUCCÈS !"
echo "============================================"
echo ""
echo "📁 Dossier d'installation :"
echo "   /content/drive/MyDrive/assistant-juridique"
echo ""
echo "🔧 CONFIGURATION OBLIGATOIRE :"
echo ""
echo "   1. Ouvrez le fichier :"
echo "      /content/drive/MyDrive/assistant-juridique/config/api_keys.yaml"
echo "      → Ajoutez votre clé GROQ_API_KEY"
echo ""
echo "   2. Ouvrez le fichier :"
echo "      /content/drive/MyDrive/assistant-juridique/config/tampon_config.yaml"
echo "      → Personnalisez vos informations"
echo ""
echo "🚀 POUR LANCER L'ASSISTANT :"
echo ""
echo "   Ouvrez et exécutez :"
echo "   /content/drive/MyDrive/assistant-juridique/launch.ipynb"
echo ""
echo "📞 Support: votre-email@domaine.com"
echo ""
echo "============================================"