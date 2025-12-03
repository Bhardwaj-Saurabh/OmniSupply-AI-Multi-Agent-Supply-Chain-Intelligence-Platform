"""
ChromaDB client for semantic search in OmniSupply platform.
Stores and retrieves embeddings for reports, insights, and historical data.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .embeddings import EmbeddingService, DocumentPreprocessor

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for OmniSupply"""

    def __init__(
        self,
        persist_directory: str = "data/chroma",
        collection_name: str = "omnisupply",
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Initialize vector store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_service: Custom embedding service (defaults to OpenAI)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding service
        self.embedding_service = embedding_service or EmbeddingService()

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "OmniSupply semantic search"}
        )

        logger.info(f"Vector store initialized: {collection_name} ({self.collection.count()} documents)")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> int:
        """
        Add documents to vector store.

        Args:
            documents: List of text documents
            metadatas: List of metadata dicts
            ids: List of unique IDs

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        logger.info(f"Adding {len(documents)} documents to vector store...")

        try:
            # Generate embeddings
            embeddings = self.embedding_service.embed_batch(documents)

            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"✅ Added {len(documents)} documents")
            return len(documents)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Semantic search for similar documents.

        Args:
            query: Search query text
            n_results: Number of results to return
            where: Metadata filters (e.g., {"type": "order"})
            where_document: Document content filters

        Returns:
            Dict with ids, documents, metadatas, distances
        """
        logger.info(f"Searching for: '{query}' (limit={n_results})")

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)

            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )

            logger.info(f"Found {len(results['ids'][0])} results")
            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise

    def delete_collection(self):
        """Delete the collection"""
        logger.warning(f"Deleting collection: {self.collection.name}")
        self.client.delete_collection(name=self.collection.name)

    def reset(self):
        """Reset the collection (delete all documents)"""
        logger.warning("Resetting vector store...")
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"description": "OmniSupply semantic search"}
        )

    def get_count(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()


class OmniSupplyVectorStore:
    """High-level vector store for OmniSupply with domain-specific methods"""

    def __init__(self, persist_directory: str = "data/chroma"):
        self.store = VectorStore(persist_directory=persist_directory)
        self.preprocessor = DocumentPreprocessor()

    def index_orders(self, orders: List[Dict]) -> int:
        """Index orders for semantic search"""
        documents = [self.preprocessor.create_order_document(o) for o in orders]
        metadatas = [{"type": "order", "order_id": o.get("order_id")} for o in orders]
        ids = [f"order_{o.get('order_id')}" for o in orders]

        return self.store.add_documents(documents, metadatas, ids)

    def index_shipments(self, shipments: List[Dict]) -> int:
        """Index shipments for semantic search"""
        documents = [self.preprocessor.create_shipment_document(s) for s in shipments]
        metadatas = [{"type": "shipment", "shipment_id": s.get("shipment_id")} for s in shipments]
        ids = [f"shipment_{s.get('shipment_id')}" for s in shipments]

        return self.store.add_documents(documents, metadatas, ids)

    def index_inventory(self, inventory: List[Dict]) -> int:
        """Index inventory for semantic search"""
        documents = [self.preprocessor.create_inventory_document(i) for i in inventory]
        metadatas = [{"type": "inventory", "sku": i.get("sku")} for i in inventory]
        ids = [f"inventory_{i.get('sku')}" for i in inventory]

        return self.store.add_documents(documents, metadatas, ids)

    def index_transactions(self, transactions: List[Dict]) -> int:
        """Index financial transactions for semantic search"""
        documents = [self.preprocessor.create_transaction_document(t) for t in transactions]
        metadatas = [{"type": "transaction", "txn_id": t.get("transaction_id")} for t in transactions]
        ids = [f"txn_{t.get('transaction_id')}" for t in transactions]

        return self.store.add_documents(documents, metadatas, ids)

    def index_report(self, report: Dict) -> int:
        """Index generated report for future retrieval"""
        document = self.preprocessor.create_report_document(report)
        metadata = {
            "type": "report",
            "report_id": report.get("report_id"),
            "report_type": report.get("report_type")
        }
        id_ = f"report_{report.get('report_id')}"

        return self.store.add_documents([document], [metadata], [id_])

    def index_alert(self, alert: Dict) -> int:
        """Index alert for historical search"""
        document = self.preprocessor.create_alert_document(alert)
        metadata = {
            "type": "alert",
            "alert_id": alert.get("alert_id"),
            "severity": alert.get("severity")
        }
        id_ = f"alert_{alert.get('alert_id')}"

        return self.store.add_documents([document], [metadata], [id_])

    def search_orders(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search orders semantically"""
        results = self.store.search(
            query=query,
            n_results=n_results,
            where={"type": "order"}
        )
        return self._format_results(results)

    def search_reports(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search historical reports"""
        results = self.store.search(
            query=query,
            n_results=n_results,
            where={"type": "report"}
        )
        return self._format_results(results)

    def search_all(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search across all document types"""
        results = self.store.search(query=query, n_results=n_results)
        return self._format_results(results)

    def _format_results(self, results: Dict) -> List[Dict]:
        """Format ChromaDB results into cleaner structure"""
        if not results['ids'] or not results['ids'][0]:
            return []

        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted

    def get_stats(self) -> Dict[str, int]:
        """Get vector store statistics"""
        # This is a simplified version - ChromaDB doesn't directly support count by metadata
        return {
            'total_documents': self.store.get_count()
        }
