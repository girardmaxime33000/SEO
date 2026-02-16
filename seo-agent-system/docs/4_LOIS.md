# Les 4 Lois Fondamentales du Système

Ce document explique en détail les 4 lois qui régissent le système d'agents SEO.

## Loi #1: Hiérarchie de Recherche Non-Négociable

### Principe
Tu cherches d'abord dans ta mémoire locale (RAG hybride), ensuite dans les docs internes, et le web en dernier recours.

### Implémentation
```
Mémoire Locale (RAG Hybride: 70% sémantique + 30% texte)
    ↓ Si insuffisant
Docs Internes
    ↓ Si insuffisant
Web (Dernier Recours)
```

### Composants
- **RAG Hybride**: 70% recherche sémantique (Voyage AI), 30% recherche texte (BM25)
- **Cache local**: TTL 24h, 500MB max
- **Seuil de suffisance**: 3 résultats minimum au-dessus du seuil de similarité

### Métriques
- **Objectif**: 80% de réduction d'appels API externes
- **Tracking**: Ratio (local_hits + internal_hits) / total_queries

### Code
Voir: `core/rag/hybrid_search.py`

---

## Loi #2: Un Agent = Un Modèle Adapté

### Principe
Pas de "super modèle" pour tout. Chaque agent a son modèle, calé sur sa charge et son domaine.

### Hiérarchie de Modèles

```
Claude 4.6 (DevOps/Infrastructure)
    └── GLM-5 (Manager SEO)
            ├── Kimi K2.5 (Content Agent)
            ├── Kimi K2.5 (Design Agent)
            ├── Kimi K2.5 (Technical Agent)
            ├── Kimi K2.5 (Link Building Agent)
            └── Kimi K2.5 (Analytics Agent)
```

### Spécialisation des Embeddings

| Agent | Embedding | Raison |
|-------|-----------|--------|
| Content, Design, Link Building | voyage-4 | Généraliste, sémantique forte |
| Technical | code-3 | Optimisé pour le code |
| Analytics | finance-2 | Optimisé pour données financières/ROI |

### Avantages
- **Coût optimisé**: Modèles légers pour tâches routinières
- **Performance**: Chaque modèle excelle dans son domaine
- **Scalabilité**: Ajout facile de nouveaux agents

### Configuration
Voir: `config/models.yaml` et `config/embeddings.yaml`

---

## Loi #3: L'Isolation des Canaux est une Feature

### Principe
Chaque agent accède uniquement aux discussions pertinentes. Un rédacteur n'écoute pas 16 devs parler de bugs.

### Canaux

| Canal | Agents avec Accès |
|-------|-------------------|
| `content` | Content Agent, Manager |
| `design` | Design Agent, Manager |
| `technical` | Technical Agent, Manager |
| `link_building` | Link Building Agent, Manager |
| `analytics` | Analytics Agent, Manager |
| `management` | Manager, DevOps |
| `devops` | DevOps (accès à tout) |

### Bénéfices
- **Réduction de bruit**: -70% de messages non pertinents
- **Réduction de tokens**: Contexte plus petit = moins de tokens
- **Focus**: Agents concentrés sur leur domaine

### Métriques
- **Token reduction**: (total_messages - avg_visible) / total_messages
- **Message filtering**: Nombre de messages filtrés par agent

### Smart Routing
Le système peut router automatiquement les messages vers les bons canaux via mots-clés.

### Code
Voir: `core/channels/isolation.py`

---

## Loi #4: Re-calcul Conditionnel

### Principe
Pas de ré-embedding systématique. Sync toutes les heures, uniquement si modification. Le code actif reste hors RAG.

### Règles de Synchronisation

1. **Intervalle**: Sync toutes les heures minimum
2. **Modification**: Re-embed uniquement si le fichier a changé (hash SHA256)
3. **Code actif**: Si 50+ commits/jour → accès temps réel via git, pas d'embedding

### Workflow

```python
for fichier in fichiers:
    if not sync_interval_reached(fichier):
        skip  # Dernière sync trop récente
    
    if not file_modified(fichier):
        skip  # Fichier inchangé
    
    if is_active_code(fichier):  # 50+ commits/jour
        use_realtime_access_via_git()
        skip_embedding()
    else:
        create_embedding()
```

### Code Actif
- **Définition**: 50+ commits/jour sur un fichier
- **Accès**: Temps réel via GitPython
- **Avantages**: 
  - Toujours à jour
  - Pas de lag d'embedding
  - Économie de compute

### Métriques
- **Sync rate**: % de fichiers synchronisés
- **Skip rate**: % de fichiers skippés (inchangés + code actif)
- **Active code files**: Nombre de fichiers en accès temps réel

### Code
Voir: `core/memory/sync_manager.py`

---

## Résultats Attendus

### Impact Global

| Loi | Métrique | Objectif | Impact |
|-----|----------|----------|--------|
| #1 | Réduction API | 80% | Coûts -80% |
| #2 | Coût moyen/query | Variable | Optimisé par domaine |
| #3 | Réduction tokens | 60-70% | Contexte -70% |
| #4 | Embeddings évités | 70%+ | Compute -70% |

### Coût Total Estimé

**Sans les 4 lois** (approche naïve):
- 1000 queries/jour
- Tous → GPT-4 + web search systématique
- ~$50-100/jour

**Avec les 4 lois**:
- 1000 queries/jour
- 80% résolues en local (Loi #1)
- Modèles adaptés (Loi #2)
- Contexte réduit (Loi #3)
- Sync optimale (Loi #4)
- ~$10-15/jour

**Économie: 80-85%**

---

## Monitoring

### Commandes

```python
# Stats d'un agent
agent.print_performance_report()

# Stats RAG
agent.search.print_stats()

# Stats Sync
agent.sync_manager.print_stats()

# Stats Isolation
agent.isolation.print_isolation_report()
```

### Dashboard DevOps

Le DevOps Agent (Claude 4.6) monitor l'ensemble:

```python
devops.monitor_performance()
devops.print_devops_dashboard()
```

---

## Extensions Futures

### Loi #5 Potentielle: Cache Partagé
- Cache Redis entre agents du même canal
- Évite re-computation pour queries similaires

### Loi #6 Potentielle: Auto-tuning
- Ajustement automatique des seuils
- ML pour prédire quand chercher dans le web
- Optimisation continue des poids hybrides

---

## Références

- `core/rag/hybrid_search.py`: Implémentation Loi #1
- `config/models.yaml`: Configuration Loi #2
- `core/channels/isolation.py`: Implémentation Loi #3
- `core/memory/sync_manager.py`: Implémentation Loi #4
- `demo_orchestration.py`: Exemple complet
