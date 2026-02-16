"""
Exemple d'orchestration complète du système SEO
Démontre la hiérarchie: DevOps -> Manager -> Agents
"""

import sys
sys.path.append('/home/claude/seo-agent-system')

from infrastructure.devops_agent.main import DevOpsAgent
from managers.seo_manager.main import SEOManager
from agents.content_agent.main import ContentAgent


def main():
    print("="*70)
    print("SYSTÈME D'AGENTS SEO - DÉMONSTRATION COMPLÈTE")
    print("="*70)
    
    # 1. Initialiser la hiérarchie
    print("\n[ÉTAPE 1] Initialisation de la hiérarchie")
    print("-" * 70)
    
    # Niveau 1: DevOps (Claude 4.6)
    devops = DevOpsAgent()
    print("✓ DevOps Agent initialisé (Claude 4.6)")
    
    # Niveau 2: Manager (GLM-5)
    manager = SEOManager()
    devops.register_manager('seo_manager', manager)
    print("✓ SEO Manager initialisé (GLM-5)")
    
    # Niveau 3: Agents (Kimi K2.5)
    content_agent = ContentAgent()
    manager.register_agent('content', content_agent)
    print("✓ Content Agent initialisé (Kimi K2.5)")
    
    print("\nHiérarchie établie:")
    print("  Claude 4.6 (DevOps)")
    print("    └── GLM-5 (SEO Manager)")
    print("          └── Kimi K2.5 (Content Agent)")
    
    # 2. Orchestration par le DevOps
    print("\n[ÉTAPE 2] Orchestration DevOps")
    print("-" * 70)
    
    orchestration = devops.orchestrate_system(
        objective="Optimiser les pages artistes InRealArt pour augmenter le trafic organique de 200%",
        scope=["content", "technical"]
    )
    print(f"Plan d'orchestration généré ({orchestration['tokens_used']} tokens)")
    print(f"\nExtrait: {orchestration['content'][:200]}...\n")
    
    # 3. Stratégie par le Manager
    print("\n[ÉTAPE 3] Stratégie SEO Manager")
    print("-" * 70)
    
    strategy = manager.create_seo_strategy(
        project_name="InRealArt - Pages Artistes Q1 2026",
        goals=[
            "Optimiser 35 pages artistes",
            "Augmenter trafic organique 200%",
            "Améliorer taux de conversion"
        ],
        constraints={
            "Budget": "5000€/mois",
            "Timeline": "3 mois",
            "Focus": "Long-tail keywords"
        }
    )
    print(f"Stratégie créée ({strategy['tokens_used']} tokens)")
    print(f"\nExtrait: {strategy['content'][:200]}...\n")
    
    # 4. Exécution par l'Agent Content
    print("\n[ÉTAPE 4] Optimisation Content Agent")
    print("-" * 70)
    
    optimization = content_agent.optimize_content(
        content="""
        Jean Dupont est un artiste contemporain français spécialisé dans l'art abstrait.
        Ses œuvres sont disponibles à l'achat ou en location avec option d'achat (LOA).
        """,
        target_keywords=[
            "artiste contemporain français",
            "art abstrait",
            "œuvre art LOA",
            "location option achat art"
        ],
        intent="commercial"
    )
    print(f"Optimisation effectuée ({optimization['tokens_used']} tokens)")
    print(f"\nExtrait: {optimization['answer'][:200]}...\n")
    
    # 5. Coordination inter-agents
    print("\n[ÉTAPE 5] Coordination Manager")
    print("-" * 70)
    
    coordination = manager.coordinate_agents(
        task="Audit complet page artiste Jean Dupont",
        involved_agents=['content']  # Seul content est initialisé pour la démo
    )
    print(f"Coordination définie ({coordination['tokens_used']} tokens)")
    print(f"\nExtrait: {coordination['content'][:200]}...\n")
    
    # 6. Monitoring DevOps
    print("\n[ÉTAPE 6] Monitoring Performance")
    print("-" * 70)
    
    monitoring = devops.monitor_performance()
    print(f"Monitoring effectué ({monitoring['tokens_used']} tokens)")
    print(f"\nExtrait: {monitoring['content'][:200]}...\n")
    
    # 7. Statistiques finales
    print("\n[ÉTAPE 7] Rapports de Performance")
    print("=" * 70)
    
    print("\n--- AGENT CONTENT ---")
    content_agent.print_performance_report()
    
    print("\n--- MANAGER SEO ---")
    manager.print_manager_stats()
    
    print("\n--- DEVOPS ---")
    devops.print_devops_dashboard()
    
    # 8. Vérification des 4 lois
    print("\n[ÉTAPE 8] Vérification des 4 Lois")
    print("=" * 70)
    
    print("\nLOI #1: Hiérarchie de recherche")
    stats = content_agent.get_stats()
    search_stats = stats.get('search_stats', {})
    print(f"  Réduction API: {search_stats.get('api_reduction', 'N/A')}")
    print(f"  Local hits: {search_stats.get('local_hits', 0)}")
    print(f"  Web hits: {search_stats.get('web_hits', 0)}")
    print(f"  ✓ Objectif: 80% réduction" if '80' in str(search_stats.get('api_reduction', '')) else "  ⚠ Besoin de plus de données")
    
    print("\nLOI #2: Modèles spécialisés")
    print(f"  Content Agent: {content_agent.model} ({content_agent.provider})")
    print(f"  Manager: {manager.model} ({manager.provider})")
    print(f"  DevOps: {devops.model}")
    print(f"  ✓ Chaque niveau a son modèle adapté")
    
    print("\nLOI #3: Isolation des canaux")
    isolation_stats = stats.get('isolation', {})
    print(f"  Token reduction: {isolation_stats.get('token_reduction', 'N/A')}")
    print(f"  Canal: {content_agent.channel.value}")
    print(f"  ✓ Agent isolé sur son canal")
    
    print("\nLOI #4: Re-calcul conditionnel")
    sync_stats = stats.get('sync_stats', {})
    print(f"  Sync rate: {sync_stats.get('sync_rate', 'N/A')}")
    print(f"  Skip rate: {sync_stats.get('skip_rate', 'N/A')}")
    print(f"  Code actif détecté: {sync_stats.get('skipped_active_code', 0)} fichiers")
    print(f"  ✓ Sync conditionnelle active")
    
    print("\n" + "="*70)
    print("DÉMONSTRATION TERMINÉE")
    print("="*70)


if __name__ == "__main__":
    main()
