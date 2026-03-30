"""Contentful-backed knowledge loader for startup-time RAG ingestion."""

from app.knowledge.contentful_loader.loader import get_contentful_documents

__all__ = ["get_contentful_documents"]
