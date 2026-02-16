"""
Sync Manager - Loi #4: Re-calcul conditionnel
- Sync toutes les heures, uniquement si modification
- Code actif (50+ commits/jour) reste hors RAG
"""

import os
import time
import hashlib
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from pathlib import Path
import git
import yaml


class SyncManager:
    """
    Gère la synchronisation conditionnelle des embeddings
    selon la Loi #4
    """
    
    def __init__(self, config_path: str = "config/embeddings.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.sync_config = config['rag_config']['sync_policy']
        self.interval_hours = self.sync_config['interval_hours']
        self.active_threshold = self.sync_config['active_code_threshold_commits_per_day']
        self.skip_active_code = self.sync_config['skip_embedding_for_active_code']
        
        # Tracking
        self.last_sync = {}
        self.file_hashes = {}
        self.commit_counts = {}
        self.active_files: Set[str] = set()
        
        # Stats
        self.stats = {
            'total_files': 0,
            'synced_files': 0,
            'skipped_unchanged': 0,
            'skipped_active_code': 0,
            'embeddings_created': 0
        }
    
    def should_sync_file(self, filepath: str, repo_path: Optional[str] = None) -> bool:
        """
        Détermine si un fichier doit être re-embedé
        
        Returns:
            True si le fichier nécessite un re-embedding
            False si skip (inchangé ou code actif)
        """
        self.stats['total_files'] += 1
        
        # Vérifier l'intervalle de temps
        if not self._sync_interval_reached(filepath):
            self.stats['skipped_unchanged'] += 1
            return False
        
        # Vérifier si le fichier a été modifié
        if not self._file_modified(filepath):
            self.stats['skipped_unchanged'] += 1
            return False
        
        # Vérifier si c'est du code actif (50+ commits/jour)
        if repo_path and self.skip_active_code:
            if self._is_active_code(filepath, repo_path):
                self.stats['skipped_active_code'] += 1
                self.active_files.add(filepath)
                return False
        
        # OK pour sync
        self.stats['synced_files'] += 1
        return True
    
    def _sync_interval_reached(self, filepath: str) -> bool:
        """Vérifie si l'intervalle de sync est atteint"""
        if filepath not in self.last_sync:
            return True
        
        elapsed = datetime.now() - self.last_sync[filepath]
        return elapsed >= timedelta(hours=self.interval_hours)
    
    def _file_modified(self, filepath: str) -> bool:
        """
        Vérifie si le fichier a été modifié depuis le dernier sync
        via comparaison de hash
        """
        if not os.path.exists(filepath):
            return False
        
        current_hash = self._compute_file_hash(filepath)
        
        if filepath not in self.file_hashes:
            self.file_hashes[filepath] = current_hash
            return True
        
        modified = current_hash != self.file_hashes[filepath]
        
        if modified:
            self.file_hashes[filepath] = current_hash
        
        return modified
    
    def _compute_file_hash(self, filepath: str) -> str:
        """Calcule le hash SHA256 du fichier"""
        sha256_hash = hashlib.sha256()
        
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _is_active_code(self, filepath: str, repo_path: str) -> bool:
        """
        Détermine si le fichier est du code actif (50+ commits/jour)
        """
        try:
            repo = git.Repo(repo_path)
            
            # Compter les commits des dernières 24h pour ce fichier
            since = datetime.now() - timedelta(days=1)
            commits = list(repo.iter_commits(
                paths=filepath,
                since=since.isoformat()
            ))
            
            commit_count = len(commits)
            self.commit_counts[filepath] = commit_count
            
            # Si 50+ commits/jour, c'est du code actif
            return commit_count >= self.active_threshold
            
        except Exception as e:
            print(f"Erreur git pour {filepath}: {e}")
            return False
    
    def mark_synced(self, filepath: str):
        """Marque un fichier comme synchronisé"""
        self.last_sync[filepath] = datetime.now()
        self.stats['embeddings_created'] += 1
    
    def get_active_files(self) -> Set[str]:
        """
        Retourne les fichiers de code actif
        Ces fichiers utilisent l'accès temps réel via git,
        pas d'embedding
        """
        return self.active_files
    
    def should_use_realtime_access(self, filepath: str) -> bool:
        """
        Détermine si on doit utiliser l'accès temps réel
        au lieu d'embeddings (pour code actif)
        """
        return filepath in self.active_files
    
    def sync_batch(
        self,
        filepaths: list[str],
        repo_path: Optional[str] = None,
        embedding_fn: callable = None
    ) -> Dict[str, any]:
        """
        Synchronise un batch de fichiers de manière conditionnelle
        
        Args:
            filepaths: Liste des fichiers à considérer
            repo_path: Chemin du repo git (pour détection code actif)
            embedding_fn: Fonction pour créer les embeddings
        
        Returns:
            Dict avec statistiques et fichiers traités
        """
        synced = []
        skipped = []
        active = []
        
        for filepath in filepaths:
            if self.should_use_realtime_access(filepath):
                active.append(filepath)
                continue
            
            if self.should_sync_file(filepath, repo_path):
                # Créer embedding si fonction fournie
                if embedding_fn:
                    embedding_fn(filepath)
                
                self.mark_synced(filepath)
                synced.append(filepath)
            else:
                skipped.append(filepath)
        
        return {
            'synced': synced,
            'skipped': skipped,
            'active_code': active,
            'stats': self.get_stats()
        }
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de synchronisation"""
        total = self.stats['total_files']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'sync_rate': f"{(self.stats['synced_files'] / total * 100):.1f}%",
            'skip_rate': f"{((self.stats['skipped_unchanged'] + self.stats['skipped_active_code']) / total * 100):.1f}%"
        }
    
    def print_stats(self):
        """Affiche les statistiques de synchronisation"""
        stats = self.get_stats()
        
        print(f"\n=== Stats Sync Conditionnelle ===")
        print(f"Total fichiers: {stats['total_files']}")
        print(f"Synchronisés: {stats['synced_files']} ({stats.get('sync_rate', '0%')})")
        print(f"Skippés (inchangés): {stats['skipped_unchanged']}")
        print(f"Skippés (code actif): {stats['skipped_active_code']}")
        print(f"Embeddings créés: {stats['embeddings_created']}")
        print(f"\n✓ Code actif détecté: {len(self.active_files)} fichiers")
        print(f"  → Accès temps réel via git")
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.stats = {
            'total_files': 0,
            'synced_files': 0,
            'skipped_unchanged': 0,
            'skipped_active_code': 0,
            'embeddings_created': 0
        }


class RealtimeCodeAccess:
    """
    Accès temps réel pour code actif via git
    Alternative aux embeddings pour fichiers 50+ commits/jour
    """
    
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
    
    def get_file_content(self, filepath: str, ref: str = 'HEAD') -> str:
        """
        Récupère le contenu d'un fichier à une ref donnée
        Accès temps réel, pas d'embedding
        """
        try:
            return self.repo.git.show(f"{ref}:{filepath}")
        except Exception as e:
            print(f"Erreur lecture {filepath}: {e}")
            return ""
    
    def get_recent_changes(self, filepath: str, hours: int = 24) -> list:
        """
        Récupère les changements récents d'un fichier
        """
        since = datetime.now() - timedelta(hours=hours)
        commits = list(self.repo.iter_commits(
            paths=filepath,
            since=since.isoformat()
        ))
        
        changes = []
        for commit in commits:
            changes.append({
                'hash': commit.hexsha,
                'author': str(commit.author),
                'date': commit.committed_datetime,
                'message': commit.message,
                'files': list(commit.stats.files.keys())
            })
        
        return changes
    
    def search_in_code(self, filepath: str, pattern: str) -> list:
        """
        Recherche un pattern dans le code temps réel
        Alternative à la recherche sémantique pour code actif
        """
        content = self.get_file_content(filepath)
        
        matches = []
        for i, line in enumerate(content.split('\n'), 1):
            if pattern.lower() in line.lower():
                matches.append({
                    'line': i,
                    'content': line,
                    'context': self._get_context(content, i)
                })
        
        return matches
    
    def _get_context(self, content: str, line_num: int, context_lines: int = 3) -> str:
        """Récupère le contexte autour d'une ligne"""
        lines = content.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end])
