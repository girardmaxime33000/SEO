"""
Content SEO Agent - Kimi K2.5
Agent spécialisé dans l'optimisation de contenu SEO
"""

from core.base_agent import BaseAgent
from typing import List


class ContentAgent(BaseAgent):
    """
    Agent de contenu SEO
    Modèle: Kimi K2.5
    Embedding: voyage-4
    Canal: content
    """
    
    def __init__(self):
        super().__init__(agent_name='content')
        
        # Capacités spécifiques
        self.capabilities = self.config['capabilities']
    
    def _get_role_description(self) -> str:
        return """un agent SEO spécialisé dans l'optimisation de contenu.
Tu es expert en:
- Recherche et ciblage de mots-clés
- Optimisation des titres et méta descriptions
- Structure de contenu (H1, H2, H3)
- Densité et placement de mots-clés
- Rédaction SEO-friendly

Réponds de manière concise et actionnable."""
    
    def _get_files_for_sync(self) -> List[str]:
        """
        Fichiers pertinents pour l'agent Content:
        - Articles de blog
        - Pages produits
        - Landing pages
        - Documentation content
        """
        # Patterns de fichiers à synchroniser
        patterns = [
            'content/**/*.md',
            'blog/**/*.html',
            'pages/**/*.html',
            'docs/**/*.md'
        ]
        
        # TODO: Implémenter la recherche de fichiers par pattern
        return []
    
    def optimize_content(
        self,
        content: str,
        target_keywords: List[str],
        intent: str = "informational"
    ) -> dict:
        """
        Optimise un contenu pour le SEO
        """
        query = f"""Optimise ce contenu pour le SEO:

Contenu:
{content}

Mots-clés cibles: {', '.join(target_keywords)}
Intent: {intent}

Fournis:
1. Un titre optimisé
2. Une méta description
3. Des suggestions de structure (H1, H2, H3)
4. Des recommandations d'amélioration
"""
        
        result = self.query(query)
        return result
    
    def analyze_keyword_opportunity(
        self,
        keyword: str,
        existing_content: str = None
    ) -> dict:
        """
        Analyse une opportunité de mot-clé
        """
        query = f"""Analyse l'opportunité SEO pour le mot-clé: "{keyword}"

{"Contenu existant à optimiser:" if existing_content else "Nouveau contenu à créer"}
{existing_content if existing_content else ""}

Fournis:
1. Intention de recherche
2. Difficulté estimée
3. Volume de recherche probable
4. Suggestions de mots-clés secondaires
5. Structure de contenu recommandée
"""
        
        result = self.query(query)
        return result
    
    def generate_meta_tags(
        self,
        page_content: str,
        primary_keyword: str
    ) -> dict:
        """
        Génère les balises meta optimisées
        """
        query = f"""Génère des balises meta optimisées pour cette page:

Contenu: {page_content[:500]}...
Mot-clé principal: {primary_keyword}

Fournis:
1. Title tag (50-60 caractères)
2. Meta description (150-160 caractères)
3. H1 tag
4. Suggestions de H2/H3
"""
        
        result = self.query(query)
        return result


if __name__ == "__main__":
    # Test de l'agent
    agent = ContentAgent()
    
    # Test 1: Optimisation de contenu
    print("\n=== Test 1: Optimisation de contenu ===")
    result = agent.optimize_content(
        content="InRealArt propose des œuvres d'art contemporain en location avec option d'achat (LOA).",
        target_keywords=["location œuvre art", "LOA art contemporain", "financement art"],
        intent="commercial"
    )
    print(f"Réponse: {result['answer'][:200]}...")
    
    # Test 2: Analyse de mot-clé
    print("\n=== Test 2: Analyse de mot-clé ===")
    result = agent.analyze_keyword_opportunity(
        keyword="simulateur LOA art"
    )
    print(f"Réponse: {result['answer'][:200]}...")
    
    # Rapport de performance
    agent.print_performance_report()
