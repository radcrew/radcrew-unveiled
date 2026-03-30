"""User-facing chat copy and tiny chat helpers."""

from __future__ import annotations

MSG_FALLBACK_LOW_CONTEXT = (
    "I don't have enough reliable information on that yet. If you'd like, email "
    "code@radcrew.org and the team can help you directly."
)
MSG_MISSING_HF_KEY = (
    "The FAQ assistant is not configured yet. Set HUGGINGFACE_API_KEY or HF_TOKEN in "
    "backend/.env (see backend/.env.example), then restart the server."
)
MSG_AI_UNAVAILABLE = (
    "The AI service is temporarily unavailable. Please try again in a moment or "
    "email code@radcrew.org."
)
