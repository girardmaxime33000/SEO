# Architecture du Système d'Agents SEO

## Vue d'Ensemble

```
╔════════════════════════════════════════════════════════════════════════╗
║                    CLAUDE 4.6 - DevOps/Infrastructure                  ║
║  • Orchestration système                                               ║
║  • Monitoring performance                                              ║
║  • Résolution de problèmes                                             ║
║  • Optimisation ressources                                             ║
╠════════════════════════════════════════════════════════════════════════╣
║                         GLM-5 - SEO Manager                            ║
║  • Stratégies SEO                                                      ║
║  • Coordination inter-agents                                           ║
║  • Décisions stratégiques                                              ║
║  • Rapports consolidés                                                 ║
╠═══════════╦═══════════╦═══════════╦═══════════╦═══════════════════════╣
║  Kimi K2.5│ Kimi K2.5 │ Kimi K2.5 │ Kimi K2.5 │    Kimi K2.5          ║
║  Content  │  Design   │ Technical │   Link    │    Analytics          ║
║           │           │           │  Building │                       ║
║ voyage-4  │ voyage-4  │  code-3   │ voyage-4  │    finance-2          ║
╚═══════════╩═══════════╩═══════════╩═══════════╩═══════════════════════╝
```

## Les 4 Lois Fondamentales

### ⚡ LOI #1: Hiérarchie de Recherche
```
┌─────────────────────────────────────┐
│  1. Mémoire Locale (RAG Hybride)    │
│     • 70% Sémantique (Voyage AI)    │
│     • 30% Texte (BM25)              │
│     ✓ 80% réduction appels API      │
├─────────────────────────────────────┤
│  2. Docs Internes                   │
│     • Base de connaissance          │
│     • Documentation projet          │
├─────────────────────────────────────┤
│  3. Web (Dernier Recours)           │
│     • Seulement si nécessaire       │
│     • Informations externes         │
└─────────────────────────────────────┘
```

### 🎯 LOI #2: Spécialisation des Modèles
```
Niveau 1: Claude 4.6    → Décisions complexes, orchestration
Niveau 2: GLM-5         → Coordination, stratégie
Niveau 3: Kimi K2.5     → Tâches spécialisées répétitives

Embeddings:
• voyage-4    → Général (content, design, link)
• code-3      → Code technique
• finance-2   → ROI, analytics
```

### 🔒 LOI #3: Isolation des Canaux
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Content  │ │  Design  │ │Technical │ │   Link   │ │Analytics │
│  Canal   │ │  Canal   │ │  Canal   │ │  Canal   │ │  Canal   │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     └────────────┴──────────┬──┴──────────┬─┴────────────┘
                             │             │
                    ┌────────▼─────┐ ┌────▼────────┐
                    │  Management  │ │   DevOps    │
                    │    Canal     │ │   Canal     │
                    │   (Manager)  │ │  (Accès à   │
                    │              │ │    tout)    │
                    └──────────────┘ └─────────────┘

Résultat: 60-70% réduction tokens
```

### 🔄 LOI #4: Re-calcul Conditionnel
```
Fichier modifié ?
     │
     ├─ Non → SKIP ✓
     │
     └─ Oui → Vérifier intervalle (1h)
              │
              ├─ Trop récent → SKIP ✓
              │
              └─ OK → Vérifier commits/jour
                       │
                       ├─ 50+ commits → Accès temps réel GIT ⚡
                       │                (pas d'embedding)
                       │
                       └─ < 50 commits → Créer embedding 📊

Résultat: 70% réduction embeddings
```

## Flux de Données

```
[Requête utilisateur]
         ↓
    [DevOps Agent] ← Orchestration globale
         ↓
    [Manager SEO] ← Stratégie & coordination
         ↓
   [Agent Spécialisé] ← Exécution
         ↓
┌────────────────────┐
│ 1. RAG Local       │ ← LOI #1: Hiérarchie
│    (70/30 hybride) │
├────────────────────┤
│ 2. Modèle adapté   │ ← LOI #2: Spécialisation
│    (K2.5)          │
├────────────────────┤
│ 3. Canal isolé     │ ← LOI #3: Isolation
│    (contexte mini) │
├────────────────────┤
│ 4. Sync smart      │ ← LOI #4: Conditionnel
│    (si modifié)    │
└────────────────────┘
         ↓
    [Réponse]
```

## Économies Réalisées

### Sans les 4 lois (approche naïve)
```
┌──────────────────────────────────────┐
│ 1000 queries/jour                    │
│ • Tous → GPT-4                       │
│ • Web search systématique            │
│ • Contexte complet non filtré        │
│ • Re-embedding automatique           │
│                                      │
│ Coût: $50-100/jour                   │
└──────────────────────────────────────┘
```

### Avec les 4 lois
```
┌──────────────────────────────────────┐
│ 1000 queries/jour                    │
│ • 80% résolu en local (Loi #1)       │
│ • Modèles optimisés (Loi #2)         │
│ • Contexte réduit 70% (Loi #3)       │
│ • Embeddings -70% (Loi #4)           │
│                                      │
│ Coût: $10-15/jour                    │
│ ÉCONOMIE: 80-85%                     │
└──────────────────────────────────────┘
```

## Métriques de Performance

```
┌─────────────────────────────────────────────────────┐
│ LOI #1 - Hiérarchie de Recherche                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80% ✓              │
│ Objectif: 80% réduction API                         │
│                                                     │
│ LOI #2 - Modèles Spécialisés                        │
│ ✓ Claude 4.6   → DevOps/Infrastructure             │
│ ✓ GLM-5        → Management                         │
│ ✓ Kimi K2.5    → Agents (x5)                        │
│                                                     │
│ LOI #3 - Isolation Canaux                           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━ 70% ✓                    │
│ Réduction tokens contexte                           │
│                                                     │
│ LOI #4 - Sync Conditionnelle                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━ 70% ✓                    │
│ Embeddings évités                                   │
└─────────────────────────────────────────────────────┘
```

## Structure des Fichiers

```
seo-agent-system/
│
├── agents/                      ← Niveau 3 (Kimi K2.5)
│   └── content_agent/
│       └── main.py
│
├── managers/                    ← Niveau 2 (GLM-5)
│   └── seo_manager/
│       └── main.py
│
├── infrastructure/              ← Niveau 1 (Claude 4.6)
│   └── devops_agent/
│       └── main.py
│
├── core/                        ← Implémentation des 4 lois
│   ├── rag/
│   │   └── hybrid_search.py    ← LOI #1
│   ├── memory/
│   │   └── sync_manager.py     ← LOI #4
│   ├── channels/
│   │   └── isolation.py        ← LOI #3
│   └── base_agent.py           ← Classe de base
│
├── config/
│   ├── models.yaml             ← LOI #2
│   └── embeddings.yaml
│
└── docs/
    ├── 4_LOIS.md
    └── DEPLOYMENT.md
```

## Quick Start

```bash
# 1. Installation
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos clés API

# 3. Démo
python demo_orchestration.py
```

## Commandes Utiles

```python
# Créer un agent
from agents.content_agent.main import ContentAgent
agent = ContentAgent()

# Optimiser du contenu
result = agent.optimize_content(
    content="Votre texte",
    target_keywords=["mot-clé 1", "mot-clé 2"]
)

# Vérifier les stats
agent.print_performance_report()
```
