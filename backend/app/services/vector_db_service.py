"""Vector database service for storing and searching embeddings."""
from typing import List, Dict, Optional, Tuple
from app.core.config import settings
from app.core.logging_config import logger


class VectorDBService:
    """Service for vector database operations."""
    
    def __init__(self):
        self.db_type = settings.VECTOR_DB_TYPE
        self._client = None
        self._collection = None
    
    def _get_chroma_client(self):
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIR,
                    settings=Settings(anonymized_telemetry=False),
                )
                # Get or create collection
                self._collection = self._client.get_or_create_collection(
                    name=settings.QDRANT_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except ImportError:
                raise ImportError("chromadb package not installed")
        return self._client, self._collection
    
    def _get_qdrant_client(self):
        """Get or create Qdrant client."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                
                self._client = QdrantClient(url=settings.QDRANT_URL)
                
                # Create collection if it doesn't exist
                try:
                    self._client.get_collection(settings.QDRANT_COLLECTION)
                except Exception:
                    self._client.create_collection(
                        collection_name=settings.QDRANT_COLLECTION,
                        vectors_config=VectorParams(
                            size=settings.EMBEDDING_DIMENSIONS,
                            distance=Distance.COSINE,
                        ),
                    )
            except ImportError:
                raise ImportError("qdrant-client package not installed")
        return self._client
    
    async def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
    ):
        """
        Add documents to vector database.
        
        Args:
            ids: List of unique IDs
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: Optional list of metadata dicts
        """
        if self.db_type == "chroma":
            client, collection = self._get_chroma_client()
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas or [{}] * len(ids),
            )
        
        elif self.db_type == "qdrant":
            client = self._get_qdrant_client()
            from qdrant_client.models import PointStruct
            
            points = [
                PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={"text": doc, **(meta or {})},
                )
                for idx, embedding, doc, meta in zip(ids, embeddings, documents, metadatas or [{}] * len(ids))
            ]
            client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=points,
            )
        else:
            raise ValueError(f"Unknown vector DB type: {self.db_type}")
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples: (document_id, score, metadata)
        """
        if self.db_type == "chroma":
            client, collection = self._get_chroma_client()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter,
            )
            # Format results
            return list(zip(
                results["ids"][0],
                [1.0 - score for score in results["distances"][0]],  # Convert distance to similarity
                results["metadatas"][0] if results["metadatas"] else [{}] * len(results["ids"][0]),
            ))
        
        elif self.db_type == "qdrant":
            client = self._get_qdrant_client()
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            search_filter = None
            if filter:
                # Convert filter to Qdrant format
                conditions = [
                    FieldCondition(key=key, match=MatchValue(value=value))
                    for key, value in filter.items()
                ]
                search_filter = Filter(must=conditions)
            
            results = client.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=search_filter,
            )
            return [
                (str(point.id), point.score, point.payload)
                for point in results
            ]
        else:
            raise ValueError(f"Unknown vector DB type: {self.db_type}")
    
    async def delete(self, ids: List[str]):
        """Delete documents by IDs."""
        if self.db_type == "chroma":
            client, collection = self._get_chroma_client()
            collection.delete(ids=ids)
        elif self.db_type == "qdrant":
            client = self._get_qdrant_client()
            client.delete(
                collection_name=settings.QDRANT_COLLECTION,
                points_selector=ids,
            )


# Singleton instance
vector_db_service = VectorDBService()
