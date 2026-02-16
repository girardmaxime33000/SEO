# Guide de Déploiement

## Installation

### 1. Cloner le repo
```bash
git clone <votre-repo>
cd seo-agent-system
```

### 2. Environnement Python
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Configuration des API Keys
```bash
cp .env.example .env
nano .env  # Éditer avec vos clés
```

Clés nécessaires:
- `ANTHROPIC_API_KEY`: Claude 4.6 (DevOps)
- `ZHIPU_API_KEY`: GLM-5 (Manager) - [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- `MOONSHOT_API_KEY`: Kimi K2.5 (Agents) - [https://platform.moonshot.cn/](https://platform.moonshot.cn/)
- `VOYAGEAI_API_KEY`: Embeddings - [https://www.voyageai.com/](https://www.voyageai.com/)

### 4. Vérification
```bash
python demo_orchestration.py
```

## Architecture des Fichiers

```
seo-agent-system/
├── agents/                    # Niveau 3: Agents spécialisés
│   └── content_agent/
│       └── main.py           # Kimi K2.5
├── managers/                  # Niveau 2: Managers
│   └── seo_manager/
│       └── main.py           # GLM-5
├── infrastructure/            # Niveau 1: DevOps
│   └── devops_agent/
│       └── main.py           # Claude 4.6
├── core/                      # Modules core
│   ├── rag/
│   │   └── hybrid_search.py  # Loi #1
│   ├── memory/
│   │   └── sync_manager.py   # Loi #4
│   ├── channels/
│   │   └── isolation.py      # Loi #3
│   └── base_agent.py         # Classe de base
├── config/
│   ├── models.yaml           # Config modèles (Loi #2)
│   └── embeddings.yaml       # Config embeddings
├── docs/
│   └── 4_LOIS.md            # Documentation lois
├── demo_orchestration.py     # Démo complète
├── requirements.txt
└── .env.example
```

## Utilisation

### Démarrer le Système Complet

```python
from infrastructure.devops_agent.main import DevOpsAgent
from managers.seo_manager.main import SEOManager
from agents.content_agent.main import ContentAgent

# 1. Init hiérarchie
devops = DevOpsAgent()
manager = SEOManager()
content_agent = ContentAgent()

# 2. Enregistrer
devops.register_manager('seo_manager', manager)
manager.register_agent('content', content_agent)

# 3. Orchestrer
devops.orchestrate_system(
    objective="Optimiser pages artistes",
    scope=["content", "technical"]
)
```

### Utiliser un Agent Directement

```python
from agents.content_agent.main import ContentAgent

agent = ContentAgent()

# Optimiser du contenu
result = agent.optimize_content(
    content="Votre contenu ici",
    target_keywords=["mot-clé 1", "mot-clé 2"],
    intent="commercial"
)

print(result['answer'])
```

### Coordonner via le Manager

```python
from managers.seo_manager.main import SEOManager

manager = SEOManager()

# Créer une stratégie
strategy = manager.create_seo_strategy(
    project_name="Mon Projet SEO",
    goals=["Augmenter trafic 200%", "Optimiser 50 pages"],
    constraints={"Budget": "5000€", "Timeline": "3 mois"}
)

# Coordonner agents
manager.coordinate_agents(
    task="Audit complet site",
    involved_agents=['content', 'technical']
)
```

## Monitoring

### Vérifier les 4 Lois

```python
# Loi #1: Hiérarchie de recherche
agent.search.print_stats()
# Objectif: 80% réduction API

# Loi #2: Modèles spécialisés
print(f"Modèle: {agent.model}")
print(f"Embedding: {agent.embedding}")

# Loi #3: Isolation canaux
agent.isolation.print_isolation_report()

# Loi #4: Re-calcul conditionnel
agent.sync_manager.print_stats()
```

### Dashboard DevOps

```python
devops = DevOpsAgent()
devops.monitor_performance()
devops.print_devops_dashboard()
```

## Ajouter un Nouvel Agent

### 1. Créer le fichier agent

```python
# agents/new_agent/main.py
from core.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name='new_agent')
    
    def _get_role_description(self) -> str:
        return "Description du rôle"
    
    def _get_files_for_sync(self):
        return []
```

### 2. Ajouter dans config/models.yaml

```yaml
agents:
  new_agent:
    model: "k2.5"
    provider: "moonshot"
    role: "New Agent Role"
    max_tokens: 2000
    temperature: 0.5
    embedding: "voyage-4"
    capabilities:
      - capability_1
      - capability_2
    reports_to: "manager"
    channel: "new_channel"
```

### 3. Enregistrer

```python
new_agent = NewAgent()
manager.register_agent('new_agent', new_agent)
```

## Optimisation des Coûts

### Budget par Modèle

| Modèle | Coût Input | Coût Output | Usage Recommandé |
|--------|------------|-------------|------------------|
| Claude 4.6 | $3/1M | $15/1M | DevOps, décisions complexes |
| GLM-5 | $0.5/1M | $0.5/1M | Coordination, stratégie |
| Kimi K2.5 | $0.12/1M | $0.12/1M | Tâches répétitives agents |
| Voyage-4 | $0.1/1M | - | Embeddings généraux |
| Code-3 | $0.11/1M | - | Code technique |
| Finance-2 | $0.12/1M | - | Données financières |

### Réduction Effective

Avec les 4 lois:
- **80% réduction** appels API (Loi #1)
- **70% réduction** tokens de contexte (Loi #3)
- **70% réduction** embeddings (Loi #4)
- **Modèles optimisés** par tâche (Loi #2)

**Économie totale: ~85%** vs approche naïve

## Troubleshooting

### Erreur: API Key Invalid
```bash
# Vérifier que les clés sont dans .env
cat .env | grep API_KEY

# Recharger l'environnement
source .env
```

### Erreur: Module not found
```bash
# Vérifier l'installation
pip list | grep voyageai

# Réinstaller si nécessaire
pip install -r requirements.txt --force-reinstall
```

### Performance Dégradée

```python
# Vérifier les stats
agent.print_performance_report()

# Si réduction API < 80%
# → Augmenter le cache local
# → Vérifier la qualité des embeddings
# → Ajuster les seuils de similarité

# Si tokens trop élevés
# → Vérifier l'isolation des canaux
# → Réduire max_tokens dans config
```

### Sync Manager Lent

```python
# Vérifier les fichiers actifs
active_files = sync_manager.get_active_files()
print(f"{len(active_files)} fichiers en accès temps réel")

# Si trop de fichiers skip embedding
# → Vérifier le seuil de commits (50/jour par défaut)
# → Ajuster dans config/embeddings.yaml
```

## Déploiement Production

### 1. Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "infrastructure/devops_agent/main.py"]
```

### 2. Variables d'environnement

```bash
# Production
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export CACHE_SIZE_MB=1000
export RATE_LIMIT_ENABLED=true
```

### 3. Monitoring

Intégrer avec:
- **Prometheus**: Métriques
- **Grafana**: Dashboards
- **Sentry**: Error tracking
- **CloudWatch**: Logs (si AWS)

### 4. Scaling

- Horizontal: Plusieurs instances d'agents
- Vertical: Augmenter max_tokens si nécessaire
- Cache partagé: Redis pour cache inter-agents

## Support

- Documentation: `docs/4_LOIS.md`
- Démo: `python demo_orchestration.py`
- Issues: Ouvrir une issue GitHub
