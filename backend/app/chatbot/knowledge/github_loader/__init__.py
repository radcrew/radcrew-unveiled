"""GitHub-backed knowledge loader for startup-time RAG ingestion."""

from app.chatbot.knowledge.github_loader.loader import get_resume_documents

__all__ = ["get_resume_documents"]
