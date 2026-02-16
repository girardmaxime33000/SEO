#!/bin/bash

# Script de déploiement sur GitHub
# Repo: https://github.com/girardmaxime33000/SEO

echo "=== Déploiement Système d'Agents SEO ==="

# 1. Télécharger et extraire l'archive
echo "[1/4] Extraction de l'archive..."
tar -xzf seo-agent-system.tar.gz
cd seo-agent-system

# 2. Initialiser git si nécessaire
echo "[2/4] Configuration Git..."
if [ ! -d ".git" ]; then
    git init
    git config user.email "maxime@inrealart.com"
    git config user.name "Maxime"
fi

# 3. Ajouter le remote GitHub
echo "[3/4] Ajout du remote GitHub..."
git remote remove origin 2>/dev/null
git remote add origin https://github.com/girardmaxime33000/SEO.git

# 4. Push vers GitHub
echo "[4/4] Push vers GitHub..."
git add -A
git commit -m "Initial commit: Système d'agents SEO multi-modèles avec 4 lois fondamentales" || echo "Already committed"
git branch -M main
git push -u origin main --force

echo ""
echo "✓ Déploiement terminé!"
echo "Repo: https://github.com/girardmaxime33000/SEO"
