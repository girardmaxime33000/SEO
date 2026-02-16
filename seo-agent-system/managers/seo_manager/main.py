"""
SEO Manager - GLM-5
Coordonne les agents SEO et prend les décisions stratégiques
"""

import os
from typing import Dict, List, Optional
import yaml
import requests
from core.channels.isolation import ChannelIsolation, Channel


class SEOManager:
    """
    Manager SEO - GLM-5
    Coordonne: Content, Design, Technical, Link Building, Analytics
    Reporte au DevOps Agent (Claude 4.6)
    """
    
    def __init__(self, config_path: str = "config/models.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['models']['manager']
        self.model = self.config['model']
        self.provider = self.config['provider']
        self.max_tokens = self.config['max_tokens']
        self.temperature = self.config['temperature']
        
        # API config
        self.api_config = config['api_config'][self.provider]
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")
        
        # Isolation des canaux
        self.isolation = ChannelIsolation(config_path)
        
        # Agents sous supervision
        self.agents = {
            'content': None,
            'design': None,
            'technical': None,
            'link_building': None,
            'analytics': None
        }
        
        # Stats
        self.stats = {
            'strategies_created': 0,
            'agents_coordinated': 0,
            'decisions_made': 0,
            'reports_generated': 0
        }
    
    def register_agent(self, agent_name: str, agent_instance):
        """Enregistre un agent sous la supervision du manager"""
        if agent_name in self.agents:
            self.agents[agent_name] = agent_instance
            print(f"✓ Agent {agent_name} enregistré")
    
    def create_seo_strategy(
        self,
        project_name: str,
        goals: List[str],
        constraints: Dict
    ) -> Dict:
        """
        Crée une stratégie SEO coordonnée
        Délègue aux agents spécialisés
        """
        self.stats['strategies_created'] += 1
        
        # Contexte des conversations de tous les agents
        context = self._gather_agent_contexts()
        
        prompt = f"""En tant que Manager SEO, crée une stratégie complète pour:

Projet: {project_name}

Objectifs:
{chr(10).join(f'- {goal}' for goal in goals)}

Contraintes:
{chr(10).join(f'- {k}: {v}' for k, v in constraints.items())}

Contexte des agents:
{context}

Fournis:
1. Plan d'action par agent (Content, Design, Technical, Link Building, Analytics)
2. Priorisation des tâches
3. Timeline
4. KPIs à suivre
5. Coordination inter-agents nécessaire
"""
        
        response = self._call_model(prompt)
        
        # Poster la stratégie sur le canal management
        self.isolation.post_message(
            channel=Channel.MANAGEMENT,
            sender='manager',
            content=response['content']
        )
        
        return response
    
    def coordinate_agents(
        self,
        task: str,
        involved_agents: List[str]
    ) -> Dict:
        """
        Coordonne plusieurs agents pour une tâche
        """
        self.stats['agents_coordinated'] += len(involved_agents)
        
        # Vérifier que les agents sont disponibles
        available = [a for a in involved_agents if self.agents.get(a)]
        
        if len(available) < len(involved_agents):
            missing = set(involved_agents) - set(available)
            return {
                'error': f"Agents non disponibles: {missing}",
                'status': 'failed'
            }
        
        # Contexte de chaque agent impliqué
        contexts = {}
        for agent_name in available:
            contexts[agent_name] = self.isolation.get_conversation_context(
                agent_name=agent_name,
                max_tokens=500
            )
        
        prompt = f"""Coordonne les agents suivants pour cette tâche:

Tâche: {task}

Agents impliqués: {', '.join(available)}

Contexte de chaque agent:
{chr(10).join(f'{name}:{chr(10)}{ctx}{chr(10)}' for name, ctx in contexts.items())}

Fournis:
1. Rôle spécifique de chaque agent
2. Ordre d'exécution
3. Points de synchronisation
4. Dépendances entre agents
5. Critères de succès
"""
        
        response = self._call_model(prompt)
        
        # Distribuer les instructions à chaque agent
        for agent_name in available:
            self.isolation.post_message(
                channel=Channel(self.agents[agent_name].channel.value),
                sender='manager',
                content=f"[COORDINATION] {task}\n\n{response['content']}"
            )
        
        return response
    
    def make_decision(
        self,
        decision_point: str,
        options: List[str],
        criteria: Dict
    ) -> Dict:
        """
        Prend une décision stratégique basée sur les données
        """
        self.stats['decisions_made'] += 1
        
        # Contexte des analytics
        analytics_context = ""
        if self.agents.get('analytics'):
            analytics_context = self.isolation.get_conversation_context(
                agent_name='analytics',
                max_tokens=1000
            )
        
        prompt = f"""Prends une décision en tant que Manager SEO:

Point de décision: {decision_point}

Options:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

Critères de décision:
{chr(10).join(f'- {k}: {v}' for k, v in criteria.items())}

Contexte Analytics:
{analytics_context}

Fournis:
1. Option recommandée (avec justification)
2. Risques identifiés
3. Plan d'implémentation
4. Métriques de suivi
"""
        
        response = self._call_model(prompt)
        
        self.isolation.post_message(
            channel=Channel.MANAGEMENT,
            sender='manager',
            content=f"[DÉCISION] {decision_point}\n\n{response['content']}"
        )
        
        return response
    
    def generate_report(
        self,
        report_type: str = "weekly",
        period: str = None
    ) -> Dict:
        """
        Génère un rapport consolidé de tous les agents
        """
        self.stats['reports_generated'] += 1
        
        # Collecter les données de tous les agents
        agent_summaries = {}
        for agent_name, agent_instance in self.agents.items():
            if agent_instance:
                # Récupérer les stats de l'agent
                stats = agent_instance.get_stats()
                
                # Résumer les activités récentes
                messages = self.isolation.get_messages_for_agent(
                    agent_name=agent_name,
                    limit=20
                )
                
                agent_summaries[agent_name] = {
                    'stats': stats,
                    'recent_activities': len(messages)
                }
        
        prompt = f"""Génère un rapport {report_type} SEO:

Période: {period or 'dernière semaine'}

Résumé par agent:
{chr(10).join(f'{name}:{chr(10)}{summary}' for name, summary in agent_summaries.items())}

Fournis:
1. Synthèse exécutive
2. Performances par agent
3. Réussites et blocages
4. Recommandations prioritaires
5. Prochaines étapes
"""
        
        response = self._call_model(prompt)
        
        # Poster le rapport sur le canal management
        self.isolation.post_message(
            channel=Channel.MANAGEMENT,
            sender='manager',
            content=f"[RAPPORT {report_type.upper()}]\n\n{response['content']}"
        )
        
        # Notifier le DevOps
        self.isolation.post_message(
            channel=Channel.DEVOPS,
            sender='manager',
            content=f"Rapport {report_type} généré et disponible sur le canal management"
        )
        
        return response
    
    def _gather_agent_contexts(self) -> str:
        """Collecte le contexte de tous les agents"""
        contexts = []
        
        for agent_name in self.agents.keys():
            context = self.isolation.get_conversation_context(
                agent_name=agent_name,
                max_tokens=300
            )
            if context:
                contexts.append(f"\n[{agent_name.upper()}]\n{context}")
        
        return "\n".join(contexts) if contexts else "Aucun contexte disponible"
    
    def _call_model(self, prompt: str) -> Dict:
        """Appel au modèle GLM-5"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(
                f"{self.api_config['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.api_config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 0)
            
            return {
                'content': content,
                'tokens_used': tokens,
                'model': self.model
            }
            
        except Exception as e:
            print(f"Erreur API GLM-5: {e}")
            return {
                'content': f"Erreur: {str(e)}",
                'tokens_used': 0,
                'model': self.model
            }
    
    def print_manager_stats(self):
        """Affiche les statistiques du manager"""
        print(f"\n{'='*60}")
        print(f"SEO MANAGER (GLM-5)")
        print(f"{'='*60}")
        print(f"Stratégies créées: {self.stats['strategies_created']}")
        print(f"Agents coordonnés: {self.stats['agents_coordinated']}")
        print(f"Décisions prises: {self.stats['decisions_made']}")
        print(f"Rapports générés: {self.stats['reports_generated']}")
        
        print(f"\n--- Agents enregistrés ---")
        for agent_name, agent_instance in self.agents.items():
            status = "✓ Actif" if agent_instance else "✗ Non enregistré"
            print(f"{agent_name}: {status}")


if __name__ == "__main__":
    # Test du manager
    manager = SEOManager()
    
    # Test: Créer une stratégie
    print("\n=== Test: Création de stratégie SEO ===")
    strategy = manager.create_seo_strategy(
        project_name="InRealArt - Optimisation Q1 2026",
        goals=[
            "Augmenter le trafic organique de 200%",
            "Optimiser 35 pages artistes",
            "Améliorer le simulateur LOA"
        ],
        constraints={
            "Budget": "5000€/mois",
            "Timeline": "3 mois",
            "Resources": "1 dev, 1 content writer"
        }
    )
    print(f"Stratégie: {strategy['content'][:300]}...")
    
    # Stats
    manager.print_manager_stats()
