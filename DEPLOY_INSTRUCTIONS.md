# Déploiement sur GitHub - Windows

## Étapes

### 1. Télécharger l'archive
Téléchargez `seo-agent-system.tar.gz` depuis Claude

### 2. Extraire l'archive
```powershell
# Avec 7-Zip ou WinRAR
# Ou avec PowerShell:
tar -xzf seo-agent-system.tar.gz
cd seo-agent-system
```

### 3. Configurer Git
```powershell
git config user.email "maxime@inrealart.com"
git config user.name "Maxime"
```

### 4. Ajouter le remote et push
```powershell
git remote add origin https://github.com/girardmaxime33000/SEO.git
git branch -M main
git push -u origin main --force
```

### Alternative: GitHub Desktop

1. Ouvrir GitHub Desktop
2. File > Add Local Repository
3. Sélectionner le dossier `seo-agent-system`
4. Publish repository
5. Choisir le repo existant `girardmaxime33000/SEO`

### Alternative: Interface Web GitHub

1. Aller sur https://github.com/girardmaxime33000/SEO
2. Cliquer sur "Add file" > "Upload files"
3. Glisser-déposer tous les fichiers du dossier `seo-agent-system`
4. Commit changes

## En cas d'erreur d'authentification

### Option 1: Personal Access Token (Recommandé)
1. GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Generate new token
3. Cocher `repo` (Full control)
4. Copier le token
5. Lors du push, utiliser le token comme mot de passe

### Option 2: SSH
```powershell
# Générer une clé SSH
ssh-keygen -t ed25519 -C "maxime@inrealart.com"

# Ajouter la clé à GitHub
# Settings > SSH and GPG keys > New SSH key
# Copier le contenu de ~/.ssh/id_ed25519.pub

# Changer le remote
git remote set-url origin git@github.com:girardmaxime33000/SEO.git
git push -u origin main
```

## Vérification

Une fois le push effectué, vérifier sur:
https://github.com/girardmaxime33000/SEO

Vous devriez voir:
- agents/
- managers/
- infrastructure/
- core/
- config/
- docs/
- README.md
- requirements.txt
- etc.
