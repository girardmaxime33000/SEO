"""
Base Agent - Intègre les 4 lois fondamentales
Classe de base pour tous les agents (Content, Design, Technical, etc.)
"""

import os
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import yaml
import requests
from core.rag.hybrid_search import HybridSearch, SearchSource
from core.memory.sync_manager import SyncManager, RealtimeCodeAccess
from core.channels.isolation import ChannelIsolation, Channel


class BaseAgent(ABC):
    """
    Agent de base respectant les 4 lois:
    1. Hiérarchie de recherche (local > internal > web)
    2. Modèle spécialisé adapté
    3. Isolation des canaux
    4. Re-calcul conditionnel
    """
    
    def __init__(
        self,
        agent_name: str,
        config_path: str = "config/models.yaml",
        embeddings_config_path: str = "config/embeddings.yaml"
    ):
        # Configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.agent_name = agent_name
        self.config = config['models']['agents'][agent_name]
        self.model = self.config['model']
        self.provider = self.config['provider']
        self.embedding = self.config['embedding']
        self.channel = Channel(self.config['channel'])
        self.max_tokens = self.config['max_tokens']
        self.temperature = self.config['temperature']
        
        # API config
        self.api_config = config['api_config'][self.provider]
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")
        
        # LOI #1: Hiérarchie de recherche
        self.search = HybridSearch(embeddings_config_path)
        
        # LOI #4: Re-calcul conditionnel
        self.sync_manager = SyncManager(embeddings_config_path)
        
        # LOI #3: Isolation des canaux
        self.isolation = ChannelIsolation(config_path)
        
        # Accès temps réel pour code actif
        self.realtime_access = None
        
        # Historique de conversation local
        self.conversation_history = []
        
        # Stats
        self.stats = {
            'queries': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'tokens_used': 0
        }
    
    def query(
        self,
        question: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Traite une requête en respectant les 4 lois
        """
        self.stats['queries'] += 1
        
        # LOI #1: Recherche avec hiérarchie stricte
        search_results = self.search.search(
            query=question,
            domain=self.agent_name,
            top_k=5
        )
        
        # Construire le contexte
        search_context = self._format_search_results(search_results)
        
        # LOI #3: Contexte de conversation isolé
        conversation_context = self.isolation.get_conversation_context(
            agent_name=self.agent_name,
            max_tokens=1000
        )
        
        # Construire le prompt
        prompt = self._build_prompt(
            question=question,
            search_context=search_context,
            conversation_context=conversation_context,
            extra_context=context
        )
        
        # LOI #2: Appel au modèle spécialisé
        response = self._call_model(prompt)
        
        # Poster la réponse sur le canal approprié
        self.isolation.post_message(
            channel=self.channel,
            sender=self.agent_name,
            content=response['content']
        )
        
        # Retourner la réponse enrichie
        return {
            'question': question,
            'answer': response['content'],
            'sources': [r.source.value for r in search_results],
            'model': self.model,
            'channel': self.channel.value,
            'tokens_used': response.get('tokens_used', 0),
            'stats': self.get_stats()
        }
    
    def _format_search_results(self, results: List) -> str:
        """Formate les résultats de recherche pour le prompt"""
        if not results:
            return "Aucun contexte pertinent trouvé."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"[Source {i} - {result.source.value}]\n"
                f"{result.content}\n"
                f"(Score: {result.score:.2f})\n"
            )
        
        return "\n".join(formatted)
    
    def _build_prompt(
        self,
        question: str,
        search_context: str,
        conversation_context: str,
        extra_context: Optional[Dict]
    ) -> str:
        """
        Construit le prompt pour le modèle
        Inclut le contexte de recherche et de conversation
        """
        role_description = self._get_role_description()
        
        prompt = f"""Tu es {role_description}

CONTEXTE DE RECHERCHE:
{search_context}

CONTEXTE DE CONVERSATION (canal {self.channel.value}):
{conversation_context}

QUESTION:
{question}

Réponds de manière concise et précise, en te basant prioritairement sur le contexte de recherche fourni.
"""
        
        if extra_context:
            prompt += f"\n\nCONTEXTE SUPPLÉMENTAIRE:\n{extra_context}\n"
        
        return prompt
    
    @abstractmethod
    def _get_role_description(self) -> str:
        """Retourne la description du rôle de l'agent"""
        pass
    
    def _call_model(self, prompt: str) -> Dict[str, Any]:
        """
        LOI #2: Appel au modèle spécialisé
        """
        self.stats['api_calls'] += 1
        
        # Headers communs
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Payload selon le provider
        payload = self._build_api_payload(prompt)
        
        # Appel API
        try:
            response = requests.post(
                f"{self.api_config['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.api_config['timeout']
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Parser la réponse selon le provider
            content, tokens = self._parse_api_response(result)
            
            self.stats['tokens_used'] += tokens
            
            return {
                'content': content,
                'tokens_used': tokens,
                'model': self.model
            }
            
        except Exception as e:
            print(f"Erreur API {self.provider}: {e}")
            return {
                'content': f"Erreur lors de l'appel au modèle: {str(e)}",
                'tokens_used': 0,
                'model': self.model
            }
    
    def _build_api_payload(self, prompt: str) -> Dict:
        """Construit le payload API selon le provider"""
        # Format compatible OpenAI (Moonshot/Kimi)
        return {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
    
    def _parse_api_response(self, response: Dict) -> tuple[str, int]:
        """Parse la réponse API (format OpenAI)"""
        content = response['choices'][0]['message']['content']
        tokens = response.get('usage', {}).get('total_tokens', 0)
        return content, tokens
    
    def sync_memory(self, repo_path: Optional[str] = None):
        """
        LOI #4: Synchronisation conditionnelle de la mémoire
        """
        # Récupérer les fichiers à synchroniser
        # (implémentation spécifique selon le domaine)
        files_to_sync = self._get_files_for_sync()
        
        # Fonction d'embedding
        def embed_file(filepath: str):
            # Lire le fichier
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Créer l'embedding via Voyage AI
            # (implémentation via self.search)
            pass
        
        # Sync conditionnel
        result = self.sync_manager.sync_batch(
            filepaths=files_to_sync,
            repo_path=repo_path,
            embedding_fn=embed_file
        )
        
        return result
    
    @abstractmethod
    def _get_files_for_sync(self) -> List[str]:
        """Retourne les fichiers à synchroniser pour cet agent"""
        pass
    
    def get_stats(self) -> Dict:
        """
        Retourne les statistiques de l'agent
        Inclut les métriques des 4 lois
        """
        return {
            'agent': self.agent_name,
            'model': self.model,
            'channel': self.channel.value,
            **self.stats,
            'search_stats': {
                'api_reduction': f"{self.search.get_api_reduction_rate():.1f}%",
                'local_hits': self.search.stats['local_hits'],
                'web_hits': self.search.stats['web_hits']
            },
            'sync_stats': self.sync_manager.get_stats(),
            'isolation': {
                'token_reduction': f"{self.isolation.calculate_token_reduction():.1f}%"
            }
        }
    
    def print_performance_report(self):
        """Affiche un rapport de performance de l'agent"""
        print(f"\n{'='*60}")
        print(f"Agent: {self.agent_name.upper()}")
        print(f"Modèle: {self.model} ({self.provider})")
        print(f"Canal: {self.channel.value}")
        print(f"{'='*60}")
        
        print(f"\nStatistiques:")
        print(f"  Queries: {self.stats['queries']}")
        print(f"  API calls: {self.stats['api_calls']}")
        print(f"  Cache hits: {self.stats['cache_hits']}")
        print(f"  Tokens utilisés: {self.stats['tokens_used']}")
        
        # LOI #1: Hiérarchie de recherche
        self.search.print_stats()
        
        # LOI #4: Sync conditionnelle
        self.sync_manager.print_stats()
        
        # LOI #3: Isolation
        print(f"\nIsolation du canal {self.channel.value}:")
        visible_messages = len(self.isolation.get_messages_for_agent(self.agent_name))
        total_messages = self.isolation.stats['total_messages']
        print(f"  Messages visibles: {visible_messages}/{total_messages}")
