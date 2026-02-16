# Système d'Agents SEO Multi-Modèles

Architecture d'agents spécialisés avec hiérarchie de modèles et RAG hybride optimisé.

## Architecture

### Hiérarchie de Modèles

```
Claude 4.6 (DevOps/Infra)
    └── GLM-5 (Managers)
            ├── Kimi K2.5 - Agent Contenu SEO
            ├── Kimi K2.5 - Agent Design
            ├── Kimi K2.5 - Agent Analyse Technique
            └── Kimi K2.5 - Agent Link Building
```

### Embeddings Spécialisés (Voyage AI)

- **voyage-4** : Défaut (contenu, design, technique)
- **finance-2** : Analyse ROI, budget SEO
- **code-3** : Agents techniques, développeurs

## Lois Fondamentales

### 1. Hiérarchie de Recherche Non-Négociable

```
Mémoire Locale (RAG Hybride)
    70% Sémantique (Voyage AI)
    30% Texte (BM25)
         ↓
Docs Internes
         ↓
Web (Dernier Recours)
```

**Impact** : 80% d'appels API supprimés

### 2. Spécialisation des Modèles

- **1 agent = 1 modèle adapté**
- Pas de "super modèle" universel
- Embeddings par domaine

### 3. Isolation des Canaux

- Cloisonnement des discussions par domaine
- Accès restreint aux conversations pertinentes
- Réduction drastique du bruit et des tokens

### 4. Re-calcul Conditionnel

- Sync toutes les heures, uniquement si modification
- Code actif (50+ commits/jour) : accès temps réel via git
- Pas d'embedding systématique

## Structure du Projet

```
seo-agent-system/
├── agents/
│   ├── content_agent/      # Kimi K2.5
│   ├── design_agent/       # Kimi K2.5
│   ├── technical_agent/    # Kimi K2.5
│   └── link_agent/         # Kimi K2.5
├── managers/
│   └── seo_manager/        # GLM-5
├── infrastructure/
│   └── devops_agent/       # Claude 4.6
├── core/
│   ├── rag/
│   │   ├── hybrid_search.py
│   │   ├── embeddings.py
│   │   └── cache.py
│   ├── memory/
│   │   ├── local_store.py
│   │   └── sync_manager.py
│   └── channels/
│       └── isolation.py
└── config/
    ├── models.yaml
    └── embeddings.yaml
```

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Configurer les clés API
python setup.py install
```

## Configuration

Voir `config/models.yaml` pour la configuration des modèles et `config/embeddings.yaml` pour les embeddings.

## Démarrage

```bash
# Lancer le DevOps agent
python infrastructure/devops_agent/main.py

# Lancer un manager
python managers/seo_manager/main.py

# Lancer un agent spécifique
python agents/content_agent/main.py
```
