"""
Embedding generation for semantic search in OmniSupply platform.
Converts text to vectors for similarity search.
"""

import os
from typing import List, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings for text"""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding service.

        Args:
            model: OpenAI embedding model
                - text-embedding-3-small: 1536 dims, fast, cheap
                - text-embedding-3-large: 3072 dims, better quality
            api_key: OpenAI API key (defaults to env var)
        """
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.dimension = 1536 if "small" in model else 3072

        logger.info(f"Initialized embedding service: {model} ({self.dimension}d)")

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )

                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(f"Generated embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")

            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                # Return zero vectors for failed batch
                embeddings.extend([[0.0] * self.dimension] * len(batch))

        return embeddings


class DocumentPreprocessor:
    """Prepare documents for embedding"""

    @staticmethod
    def create_order_document(order: dict) -> str:
        """Create searchable text from order"""
        return f"""
        Order {order.get('order_id')} in {order.get('category')} category.
        Customer segment: {order.get('segment')}.
        Location: {order.get('city')}, {order.get('state')}, {order.get('region')}.
        Product: {order.get('product_id')} ({order.get('sub_category')}).
        Sale price: ${order.get('sale_price')}, Profit: ${order.get('profit')}.
        Discount: {order.get('discount_percent')}%.
        Shipped via {order.get('ship_mode')}.
        {"Returned" if order.get('is_returned') else "Not returned"}.
        """

    @staticmethod
    def create_shipment_document(shipment: dict) -> str:
        """Create searchable text from shipment"""
        return f"""
        Shipment {shipment.get('shipment_id')} via {shipment.get('carrier')}.
        Route: {shipment.get('origin_port')} to {shipment.get('destination_port')}.
        Status: {shipment.get('status')}.
        Freight cost: ${shipment.get('freight_cost')}.
        Weight: {shipment.get('weight_kg')} kg.
        Delay reason: {shipment.get('delay_reason', 'None')}.
        """

    @staticmethod
    def create_inventory_document(item: dict) -> str:
        """Create searchable text from inventory item"""
        return f"""
        SKU {item.get('sku')}: {item.get('product_name')}.
        Category: {item.get('category')}.
        Warehouse: {item.get('warehouse_location')}.
        Stock: {item.get('stock_quantity')} units.
        Reorder level: {item.get('reorder_level')}.
        Unit cost: ${item.get('unit_cost')}.
        Supplier: {item.get('supplier_id')}.
        Lead time: {item.get('lead_time_days')} days.
        {"Critical stock level" if item.get('stock_quantity', 0) <= item.get('reorder_level', 0) else "Adequate stock"}.
        """

    @staticmethod
    def create_transaction_document(txn: dict) -> str:
        """Create searchable text from financial transaction"""
        return f"""
        Transaction {txn.get('transaction_id')} - {txn.get('transaction_type')}.
        Category: {txn.get('category')}, Subcategory: {txn.get('subcategory', 'N/A')}.
        Amount: ${txn.get('amount')} {txn.get('currency')}.
        Cost center: {txn.get('cost_center', 'N/A')}.
        Business unit: {txn.get('business_unit', 'N/A')}.
        Vendor: {txn.get('vendor_id', 'N/A')}.
        Notes: {txn.get('notes', 'None')}.
        """

    @staticmethod
    def create_report_document(report: dict) -> str:
        """Create searchable text from generated report"""
        return f"""
        Report Type: {report.get('report_type')}.
        Period: {report.get('period_start')} to {report.get('period_end')}.
        Agents used: {report.get('agents_used')}.
        Insights: {report.get('insights_count')} insights generated.
        Recommendations: {report.get('recommendations_count')} actions recommended.
        Summary: {report.get('summary', '')[:500]}
        """

    @staticmethod
    def create_alert_document(alert: dict) -> str:
        """Create searchable text from alert"""
        return f"""
        Alert: {alert.get('title')} ({alert.get('severity')}).
        Type: {alert.get('alert_type')}.
        Description: {alert.get('description')}.
        Affected entities: {alert.get('affected_entities')}.
        Stakeholders notified: {alert.get('stakeholders')}.
        Status: {"Acknowledged" if alert.get('acknowledged_at') else "Pending"}.
        """
