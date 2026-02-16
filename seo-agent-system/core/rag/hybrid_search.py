"""
RAG Hybride - Loi #1: Hiérarchie de recherche non-négociable
70% sémantique (Voyage AI) + 30% texte (BM25)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import voyageai
from rank_bm25 import BM25Okapi
import yaml


class SearchSource(Enum):
    LOCAL_MEMORY = "local_memory"
    INTERNAL_DOCS = "internal_docs"
    WEB = "web"


@dataclass
class SearchResult:
    content: str
    score: float
    source: SearchSource
    metadata: Dict


class HybridSearch:
    """
    Implémente la hiérarchie de recherche:
    1. Mémoire locale (RAG hybride)
    2. Docs internes
    3. Web (dernier recours)
    """
    
    def __init__(self, config_path: str = "config/embeddings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.rag_config = self.config['rag_config']
        self.semantic_weight = self.rag_config['hybrid_weights']['semantic']
        self.text_weight = self.rag_config['hybrid_weights']['text']
        
        # Voyage AI client
        self.voyage_client = voyageai.Client()
        
        # BM25 index
        self.bm25_index = None
        self.documents = []
        self.embeddings_cache = {}
        
        # Stats pour vérifier la réduction de 80% d'API calls
        self.stats = {
            'local_hits': 0,
            'internal_hits': 0,
            'web_hits': 0,
            'total_queries': 0
        }
    
    def search(
        self,
        query: str,
        domain: str,
        top_k: int = 5,
        threshold: float = None
    ) -> List[SearchResult]:
        """
        Recherche avec hiérarchie stricte:
        1. Local memory first
        2. Internal docs si insuffisant
        3. Web en dernier recours
        """
        self.stats['total_queries'] += 1
        
        # Seuil de similarité par domaine
        if threshold is None:
            threshold = self.config['domain_configs'][domain]['similarity_threshold']
        
        # ÉTAPE 1: Mémoire locale (RAG Hybride)
        local_results = self._search_local_memory(query, domain, top_k, threshold)
        
        if self._is_sufficient(local_results, threshold):
            self.stats['local_hits'] += 1
            return local_results
        
        # ÉTAPE 2: Docs internes
        internal_results = self._search_internal_docs(query, domain, top_k, threshold)
        
        if self._is_sufficient(internal_results, threshold):
            self.stats['internal_hits'] += 1
            return internal_results
        
        # ÉTAPE 3: Web (dernier recours)
        self.stats['web_hits'] += 1
        web_results = self._search_web(query, domain, top_k)
        
        return web_results
    
    def _search_local_memory(
        self,
        query: str,
        domain: str,
        top_k: int,
        threshold: float
    ) -> List[SearchResult]:
        """
        RAG Hybride: 70% sémantique + 30% texte
        """
        embedding_model = self.config['domain_configs'][domain]['embedding']
        
        # Recherche sémantique (70%)
        semantic_results = self._semantic_search(query, embedding_model, top_k * 2)
        
        # Recherche texte BM25 (30%)
        text_results = self._bm25_search(query, top_k * 2)
        
        # Fusion hybride avec poids 70/30
        hybrid_results = self._hybrid_fusion(
            semantic_results,
            text_results,
            self.semantic_weight,
            self.text_weight,
            top_k
        )
        
        # Filtrer par seuil
        return [r for r in hybrid_results if r.score >= threshold]
    
    def _semantic_search(
        self,
        query: str,
        embedding_model: str,
        top_k: int
    ) -> List[SearchResult]:
        """Recherche sémantique avec Voyage AI"""
        
        # Embedding de la requête
        query_embedding = self._get_embedding(query, embedding_model)
        
        # Calcul des similarités cosinus
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings_cache.get(embedding_model, [])):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity))
        
        # Top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similarities = similarities[:top_k]
        
        return [
            SearchResult(
                content=self.documents[idx],
                score=score,
                source=SearchSource.LOCAL_MEMORY,
                metadata={'method': 'semantic', 'model': embedding_model}
            )
            for idx, score in top_similarities
        ]
    
    def _bm25_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Recherche texte avec BM25"""
        if self.bm25_index is None:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Top K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [
            SearchResult(
                content=self.documents[idx],
                score=float(scores[idx]),
                source=SearchSource.LOCAL_MEMORY,
                metadata={'method': 'bm25'}
            )
            for idx in top_indices
        ]
    
    def _hybrid_fusion(
        self,
        semantic_results: List[SearchResult],
        text_results: List[SearchResult],
        semantic_weight: float,
        text_weight: float,
        top_k: int
    ) -> List[SearchResult]:
        """
        Fusion des résultats avec pondération 70/30
        """
        # Normaliser les scores
        all_results = {}
        
        for result in semantic_results:
            key = result.content[:100]  # Clé basée sur début du contenu
            all_results[key] = {
                'content': result.content,
                'score': result.score * semantic_weight,
                'source': result.source,
                'metadata': result.metadata
            }
        
        for result in text_results:
            key = result.content[:100]
            if key in all_results:
                # Additionner les scores pondérés
                all_results[key]['score'] += result.score * text_weight
            else:
                all_results[key] = {
                    'content': result.content,
                    'score': result.score * text_weight,
                    'source': result.source,
                    'metadata': result.metadata
                }
        
        # Trier par score hybride
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:top_k]
        
        return [
            SearchResult(
                content=r['content'],
                score=r['score'],
                source=r['source'],
                metadata=r['metadata']
            )
            for r in sorted_results
        ]
    
    def _search_internal_docs(
        self,
        query: str,
        domain: str,
        top_k: int,
        threshold: float
    ) -> List[SearchResult]:
        """Recherche dans les docs internes"""
        # Implémentation similaire au local memory
        # mais sur corpus de docs internes
        return []
    
    def _search_web(self, query: str, domain: str, top_k: int) -> List[SearchResult]:
        """Web en dernier recours"""
        return []
    
    def _get_embedding(self, text: str, model: str) -> np.ndarray:
        """Obtenir embedding avec cache"""
        cache_key = f"{model}:{hash(text)}"
        
        if cache_key not in self.embeddings_cache:
            # Appel Voyage AI
            result = self.voyage_client.embed(
                texts=[text],
                model=model
            )
            self.embeddings_cache[cache_key] = np.array(result.embeddings[0])
        
        return self.embeddings_cache[cache_key]
    
    def _is_sufficient(self, results: List[SearchResult], threshold: float) -> bool:
        """
        Détermine si les résultats sont suffisants
        pour éviter de continuer la hiérarchie de recherche
        """
        if not results:
            return False
        
        # Au moins 3 résultats au-dessus du seuil
        good_results = [r for r in results if r.score >= threshold]
        return len(good_results) >= 3
    
    def get_api_reduction_rate(self) -> float:
        """
        Calcule le taux de réduction d'appels API
        Objectif: 80%
        """
        if self.stats['total_queries'] == 0:
            return 0.0
        
        avoided = self.stats['local_hits'] + self.stats['internal_hits']
        return (avoided / self.stats['total_queries']) * 100
    
    def print_stats(self):
        """Affiche les statistiques de réduction d'API"""
        total = self.stats['total_queries']
        if total == 0:
            print("Aucune requête effectuée")
            return
        
        print(f"\n=== Stats RAG Hybride ===")
        print(f"Total requêtes: {total}")
        print(f"Local memory: {self.stats['local_hits']} ({self.stats['local_hits']/total*100:.1f}%)")
        print(f"Internal docs: {self.stats['internal_hits']} ({self.stats['internal_hits']/total*100:.1f}%)")
        print(f"Web: {self.stats['web_hits']} ({self.stats['web_hits']/total*100:.1f}%)")
        print(f"\n✓ Réduction API: {self.get_api_reduction_rate():.1f}%")
        print(f"  Objectif: 80%")
