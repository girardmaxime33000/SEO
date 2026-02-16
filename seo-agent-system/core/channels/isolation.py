"""
Channel Isolation - Loi #3: L'isolation des canaux est une feature
Chaque agent accède uniquement aux discussions pertinentes
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum
import yaml


class Channel(Enum):
    CONTENT = "content"
    DESIGN = "design"
    TECHNICAL = "technical"
    LINK_BUILDING = "link_building"
    ANALYTICS = "analytics"
    MANAGEMENT = "management"
    DEVOPS = "devops"


@dataclass
class Message:
    id: str
    channel: Channel
    sender: str
    content: str
    timestamp: float
    mentions: List[str]
    metadata: Dict


class ChannelIsolation:
    """
    Gère l'isolation stricte des canaux de communication
    Réduit drastiquement le bruit et les tokens
    """
    
    def __init__(self, config_path: str = "config/models.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Mapping agent -> channel
        self.agent_channels = {}
        for agent_name, agent_config in config['models']['agents'].items():
            self.agent_channels[agent_name] = Channel(agent_config['channel'])
        
        # Canaux spéciaux
        self.agent_channels['manager'] = Channel.MANAGEMENT
        self.agent_channels['devops'] = Channel.DEVOPS
        
        # Messages par canal
        self.channels: Dict[Channel, List[Message]] = {
            channel: [] for channel in Channel
        }
        
        # Accès cross-channel autorisés
        self.cross_channel_access = self._define_access_rules()
        
        # Stats
        self.stats = {
            'total_messages': 0,
            'filtered_messages': 0,
            'token_reduction_percent': 0
        }
    
    def _define_access_rules(self) -> Dict[str, Set[Channel]]:
        """
        Définit les règles d'accès cross-channel
        Par défaut, un agent ne voit que son canal
        """
        return {
            # Agents voient uniquement leur canal
            'content': {Channel.CONTENT, Channel.MANAGEMENT},
            'design': {Channel.DESIGN, Channel.MANAGEMENT},
            'technical': {Channel.TECHNICAL, Channel.MANAGEMENT},
            'link_building': {Channel.LINK_BUILDING, Channel.MANAGEMENT},
            'analytics': {Channel.ANALYTICS, Channel.MANAGEMENT},
            
            # Manager voit tous les canaux métier
            'manager': {
                Channel.CONTENT,
                Channel.DESIGN,
                Channel.TECHNICAL,
                Channel.LINK_BUILDING,
                Channel.ANALYTICS,
                Channel.MANAGEMENT
            },
            
            # DevOps voit tout
            'devops': set(Channel)
        }
    
    def post_message(
        self,
        channel: Channel,
        sender: str,
        content: str,
        mentions: List[str] = None,
        metadata: Dict = None
    ) -> Message:
        """Poste un message sur un canal"""
        import time
        
        message = Message(
            id=f"{channel.value}_{int(time.time())}_{len(self.channels[channel])}",
            channel=channel,
            sender=sender,
            content=content,
            timestamp=time.time(),
            mentions=mentions or [],
            metadata=metadata or {}
        )
        
        self.channels[channel].append(message)
        self.stats['total_messages'] += 1
        
        return message
    
    def get_messages_for_agent(
        self,
        agent_name: str,
        limit: Optional[int] = None,
        since_timestamp: Optional[float] = None
    ) -> List[Message]:
        """
        Récupère les messages visibles pour un agent
        selon les règles d'isolation
        """
        allowed_channels = self.cross_channel_access.get(agent_name, set())
        
        # Collecter les messages des canaux autorisés
        messages = []
        for channel in allowed_channels:
            messages.extend(self.channels[channel])
        
        # Filtrer par timestamp
        if since_timestamp:
            messages = [m for m in messages if m.timestamp > since_timestamp]
        
        # Trier par timestamp
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Limiter
        if limit:
            messages = messages[:limit]
        
        # Stats de filtrage
        total_messages = sum(len(msgs) for msgs in self.channels.values())
        filtered = total_messages - len(messages)
        self.stats['filtered_messages'] += filtered
        
        return messages
    
    def get_conversation_context(
        self,
        agent_name: str,
        max_tokens: int = 2000
    ) -> str:
        """
        Construit le contexte de conversation pour un agent
        Limite stricte de tokens via isolation
        """
        messages = self.get_messages_for_agent(agent_name, limit=50)
        
        # Construire le contexte
        context_parts = []
        current_tokens = 0
        
        for msg in messages:
            # Estimation grossière: 1 token ≈ 4 chars
            msg_tokens = len(msg.content) // 4
            
            if current_tokens + msg_tokens > max_tokens:
                break
            
            context_parts.append(
                f"[{msg.channel.value}] {msg.sender}: {msg.content}"
            )
            current_tokens += msg_tokens
        
        return "\n".join(context_parts)
    
    def calculate_token_reduction(self) -> float:
        """
        Calcule la réduction de tokens grâce à l'isolation
        Compare: tous les messages vs messages filtrés par agent
        """
        total_messages = self.stats['total_messages']
        if total_messages == 0:
            return 0.0
        
        # Moyenne de messages vus par agent (hors devops qui voit tout)
        agents_to_check = [a for a in self.agent_channels.keys() if a != 'devops']
        
        total_visible = 0
        for agent in agents_to_check:
            visible = len(self.get_messages_for_agent(agent))
            total_visible += visible
        
        avg_visible = total_visible / len(agents_to_check) if agents_to_check else 0
        
        # Réduction = (messages totaux - moyenne visible) / messages totaux
        reduction = ((total_messages - avg_visible) / total_messages) * 100
        
        self.stats['token_reduction_percent'] = reduction
        return reduction
    
    def get_channel_stats(self) -> Dict:
        """Statistiques par canal"""
        stats = {}
        
        for channel, messages in self.channels.items():
            stats[channel.value] = {
                'message_count': len(messages),
                'unique_senders': len(set(m.sender for m in messages))
            }
        
        return stats
    
    def print_isolation_report(self):
        """Affiche un rapport sur l'isolation des canaux"""
        print(f"\n=== Rapport Isolation des Canaux ===")
        print(f"Total messages: {self.stats['total_messages']}")
        print(f"Messages filtrés: {self.stats['filtered_messages']}")
        
        token_reduction = self.calculate_token_reduction()
        print(f"\n✓ Réduction de tokens: {token_reduction:.1f}%")
        
        print(f"\n--- Messages par canal ---")
        for channel, stats in self.get_channel_stats().items():
            print(f"{channel}: {stats['message_count']} messages, {stats['unique_senders']} agents")
        
        print(f"\n--- Visibilité par agent ---")
        for agent, channels in self.cross_channel_access.items():
            channel_names = [c.value for c in channels]
            visible_count = len(self.get_messages_for_agent(agent))
            print(f"{agent}: {len(channels)} canaux ({', '.join(channel_names)}) = {visible_count} messages")


class SmartRouter:
    """
    Route intelligemment les messages vers les bons canaux
    Évite le spam cross-channel
    """
    
    def __init__(self, isolation: ChannelIsolation):
        self.isolation = isolation
        
        # Mots-clés par canal pour routing automatique
        self.channel_keywords = {
            Channel.CONTENT: {
                'content', 'article', 'blog', 'keyword', 'meta',
                'title', 'description', 'h1', 'h2', 'rédaction'
            },
            Channel.DESIGN: {
                'design', 'ux', 'ui', 'mobile', 'vitals', 'speed',
                'performance', 'layout', 'responsive', 'accessibility'
            },
            Channel.TECHNICAL: {
                'technical', 'schema', 'robots', 'sitemap', 'crawl',
                'index', 'canonical', 'redirect', 'structured data'
            },
            Channel.LINK_BUILDING: {
                'link', 'backlink', 'outreach', 'partnership', 'guest',
                'anchor', 'domain authority', 'referring domains'
            },
            Channel.ANALYTICS: {
                'analytics', 'roi', 'conversion', 'traffic', 'revenue',
                'kpi', 'metric', 'performance', 'budget', 'cost'
            }
        }
    
    def route_message(self, content: str, sender: str) -> List[Channel]:
        """
        Détermine automatiquement le(s) canal(aux) approprié(s)
        pour un message
        """
        content_lower = content.lower()
        
        # Scorer chaque canal
        scores = {}
        for channel, keywords in self.channel_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[channel] = score
        
        # Si aucun match, utiliser le canal par défaut de l'agent
        if not scores:
            agent_channel = self.isolation.agent_channels.get(sender)
            return [agent_channel] if agent_channel else [Channel.MANAGEMENT]
        
        # Retourner les canaux avec le score max
        max_score = max(scores.values())
        return [ch for ch, score in scores.items() if score == max_score]
    
    def smart_post(self, sender: str, content: str) -> List[Message]:
        """
        Poste intelligemment un message sur le(s) bon(s) canal(aux)
        """
        channels = self.route_message(content, sender)
        
        messages = []
        for channel in channels:
            msg = self.isolation.post_message(
                channel=channel,
                sender=sender,
                content=content,
                metadata={'routed_by': 'smart_router'}
            )
            messages.append(msg)
        
        return messages
