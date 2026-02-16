"""
DevOps/Infrastructure Agent - Claude 4.6
Niveau supérieur de la hiérarchie
Orchestre managers et infrastructure
"""

import os
from typing import Dict, List, Optional
import yaml
from anthropic import Anthropic
from core.channels.isolation import ChannelIsolation, Channel


class DevOpsAgent:
    """
    Agent DevOps/Infrastructure - Claude 4.6
    - Orchestre le SEO Manager (GLM-5)
    - Gère l'infrastructure
    - Monitoring et déploiement
    - Gestion des ressources
    """
    
    def __init__(self, config_path: str = "config/models.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['models']['devops']
        self.model = "claude-sonnet-4-20250514"  # Claude 4.6
        self.max_tokens = self.config['max_tokens']
        self.temperature = self.config['temperature']
        
        # Client Anthropic
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Isolation des canaux (accès à tous)
        self.isolation = ChannelIsolation(config_path)
        
        # Managers supervisés
        self.managers = {
            'seo_manager': None
        }
        
        # Infrastructure state
        self.infrastructure = {
            'status': 'healthy',
            'agents_active': 0,
            'api_usage': {},
            'storage_usage': {},
            'performance_metrics': {}
        }
        
        # Stats
        self.stats = {
            'deployments': 0,
            'orchestrations': 0,
            'issues_resolved': 0,
            'optimizations': 0
        }
    
    def register_manager(self, manager_name: str, manager_instance):
        """Enregistre un manager sous la supervision DevOps"""
        if manager_name in self.managers:
            self.managers[manager_name] = manager_instance
            print(f"✓ Manager {manager_name} enregistré sous DevOps")
    
    def orchestrate_system(
        self,
        objective: str,
        scope: List[str] = None
    ) -> Dict:
        """
        Orchestre l'ensemble du système pour atteindre un objectif
        """
        self.stats['orchestrations'] += 1
        
        # Collecter l'état complet du système
        system_state = self._gather_system_state()
        
        prompt = f"""En tant qu'Agent DevOps, orchestre le système pour atteindre cet objectif:

OBJECTIF: {objective}

PÉRIMÈTRE: {', '.join(scope) if scope else 'Tous les agents'}

ÉTAT DU SYSTÈME:
{system_state}

MANAGERS DISPONIBLES:
- SEO Manager (GLM-5): Coordonne Content, Design, Technical, Link Building, Analytics

FOURNIS UN PLAN D'ORCHESTRATION:
1. Stratégie globale
2. Délégation aux managers/agents
3. Configuration infrastructure requise
4. Points de monitoring
5. Plan de rollback si nécessaire
6. Timeline et jalons
"""
        
        response = self._call_claude(prompt)
        
        # Poster sur le canal DevOps
        self.isolation.post_message(
            channel=Channel.DEVOPS,
            sender='devops',
            content=f"[ORCHESTRATION] {objective}\n\n{response['content']}"
        )
        
        return response
    
    def deploy_optimization(
        self,
        optimization_type: str,
        target: str,
        parameters: Dict
    ) -> Dict:
        """
        Déploie une optimisation système
        Ex: Ajuster les rate limits, modifier la config RAG, etc.
        """
        self.stats['deployments'] += 1
        
        prompt = f"""Déploie cette optimisation système:

TYPE: {optimization_type}
CIBLE: {target}
PARAMÈTRES: {parameters}

ÉTAT ACTUEL:
{self._get_current_config(target)}

FOURNIS:
1. Plan de déploiement étape par étape
2. Risques identifiés
3. Rollback procedure
4. Métriques de validation
5. Configuration modifiée
"""
        
        response = self._call_claude(prompt)
        
        # Logger le déploiement
        self.isolation.post_message(
            channel=Channel.DEVOPS,
            sender='devops',
            content=f"[DÉPLOIEMENT] {optimization_type} sur {target}\n\n{response['content']}"
        )
        
        return response
    
    def monitor_performance(self) -> Dict:
        """
        Monitor les performances de l'ensemble du système
        Vérifie les 4 lois
        """
        # Collecter les métriques de tous les agents
        metrics = self._collect_all_metrics()
        
        prompt = f"""Analyse les performances du système SEO:

MÉTRIQUES COLLECTÉES:
{metrics}

LOIS À VÉRIFIER:
1. Hiérarchie de recherche: Objectif 80% réduction API
2. Modèles spécialisés: Performance par agent
3. Isolation canaux: Réduction tokens
4. Re-calcul conditionnel: Taux de skip

FOURNIS:
1. Analyse de conformité aux 4 lois
2. Goulots d'étranglement identifiés
3. Recommandations d'optimisation
4. Alertes si dégradation
5. Prédictions de scaling
"""
        
        response = self._call_claude(prompt)
        
        # Poster le rapport de monitoring
        self.isolation.post_message(
            channel=Channel.DEVOPS,
            sender='devops',
            content=f"[MONITORING] Rapport de performance\n\n{response['content']}"
        )
        
        return response
    
    def resolve_issue(
        self,
        issue: str,
        context: Dict
    ) -> Dict:
        """
        Résout un problème système
        """
        self.stats['issues_resolved'] += 1
        
        prompt = f"""Résous ce problème système:

PROBLÈME: {issue}

CONTEXTE:
{context}

LOGS PERTINENTS:
{self._get_relevant_logs()}

FOURNIS:
1. Diagnostic du problème
2. Cause racine
3. Solution immédiate
4. Fix permanent
5. Prévention future
"""
        
        response = self._call_claude(prompt)
        
        # Logger la résolution
        self.isolation.post_message(
            channel=Channel.DEVOPS,
            sender='devops',
            content=f"[RÉSOLUTION] {issue}\n\n{response['content']}"
        )
        
        return response
    
    def optimize_resources(
        self,
        resource_type: str,
        usage_data: Dict
    ) -> Dict:
        """
        Optimise l'utilisation des ressources
        Ex: API quotas, storage, compute
        """
        self.stats['optimizations'] += 1
        
        prompt = f"""Optimise l'utilisation des ressources:

RESSOURCE: {resource_type}

DONNÉES D'UTILISATION:
{usage_data}

CONTRAINTES:
- Coût: Minimiser
- Performance: Maintenir
- Scalabilité: Prévoir croissance 3x

FOURNIS:
1. Analyse de l'utilisation actuelle
2. Inefficacités identifiées
3. Plan d'optimisation
4. Économies projetées
5. Risques et mitigations
"""
        
        response = self._call_claude(prompt)
        
        return response
    
    def _gather_system_state(self) -> str:
        """Collecte l'état complet du système"""
        state = []
        
        # État des managers
        for manager_name, manager_instance in self.managers.items():
            if manager_instance:
                state.append(f"{manager_name}: Actif")
                # Stats du manager si disponibles
                if hasattr(manager_instance, 'stats'):
                    state.append(f"  Stats: {manager_instance.stats}")
        
        # État de l'infrastructure
        state.append(f"\nInfrastructure: {self.infrastructure['status']}")
        state.append(f"Agents actifs: {self.infrastructure['agents_active']}")
        
        return "\n".join(state)
    
    def _collect_all_metrics(self) -> str:
        """Collecte les métriques de tous les agents"""
        metrics = []
        
        # Métriques des managers
        for manager_name, manager_instance in self.managers.items():
            if manager_instance and hasattr(manager_instance, 'agents'):
                for agent_name, agent_instance in manager_instance.agents.items():
                    if agent_instance and hasattr(agent_instance, 'get_stats'):
                        stats = agent_instance.get_stats()
                        metrics.append(f"{agent_name}: {stats}")
        
        # Métriques d'infrastructure
        metrics.append(f"\nInfrastructure Metrics:")
        metrics.append(f"API Usage: {self.infrastructure['api_usage']}")
        metrics.append(f"Storage: {self.infrastructure['storage_usage']}")
        
        return "\n".join(metrics)
    
    def _get_current_config(self, target: str) -> str:
        """Récupère la configuration actuelle d'une cible"""
        # TODO: Implémenter la récupération de config
        return f"Configuration actuelle de {target}"
    
    def _get_relevant_logs(self) -> str:
        """Récupère les logs pertinents"""
        # TODO: Implémenter la récupération de logs
        return "Logs du système"
    
    def _call_claude(self, prompt: str) -> Dict:
        """Appel à Claude 4.6"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            tokens = message.usage.input_tokens + message.usage.output_tokens
            
            return {
                'content': content,
                'tokens_used': tokens,
                'model': self.model
            }
            
        except Exception as e:
            print(f"Erreur API Claude: {e}")
            return {
                'content': f"Erreur: {str(e)}",
                'tokens_used': 0,
                'model': self.model
            }
    
    def print_devops_dashboard(self):
        """Affiche le dashboard DevOps"""
        print(f"\n{'='*60}")
        print(f"DEVOPS DASHBOARD (CLAUDE 4.6)")
        print(f"{'='*60}")
        
        print(f"\n--- INFRASTRUCTURE ---")
        print(f"Status: {self.infrastructure['status']}")
        print(f"Agents actifs: {self.infrastructure['agents_active']}")
        
        print(f"\n--- MANAGERS ---")
        for manager_name, manager_instance in self.managers.items():
            status = "✓ Actif" if manager_instance else "✗ Non enregistré"
            print(f"{manager_name}: {status}")
        
        print(f"\n--- OPÉRATIONS ---")
        print(f"Déploiements: {self.stats['deployments']}")
        print(f"Orchestrations: {self.stats['orchestrations']}")
        print(f"Problèmes résolus: {self.stats['issues_resolved']}")
        print(f"Optimisations: {self.stats['optimizations']}")


if __name__ == "__main__":
    # Test du DevOps Agent
    devops = DevOpsAgent()
    
    # Test: Orchestration système
    print("\n=== Test: Orchestration système ===")
    result = devops.orchestrate_system(
        objective="Optimiser le système SEO pour InRealArt avec focus sur pages artistes",
        scope=["content", "technical", "analytics"]
    )
    print(f"Plan d'orchestration: {result['content'][:300]}...")
    
    # Dashboard
    devops.print_devops_dashboard()
