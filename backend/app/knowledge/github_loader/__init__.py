"""GitHub-backed knowledge loader for startup-time RAG ingestion."""

from app.knowledge.github_loader.loader import get_github_markdown_documents

__all__ = ["get_github_markdown_documents"]
