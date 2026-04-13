"""User-facing chat copy and tiny chat helpers."""

from __future__ import annotations

MSG_FALLBACK_LOW_CONTEXT = (
    "I don't have enough reliable information on that yet. If you'd like, email "
    "code@radcrew.org and the team can help you directly."
)
MSG_AI_UNAVAILABLE = (
    "The AI service is temporarily unavailable. Please try again in a moment or "
    "email code@radcrew.org."
)
MSG_FEEDBACK_SEND_FAILED = (
    "We couldn't send your feedback right now. Please try again later or email {email}."
)
MSG_FEEDBACK_THANKS = (
    "Thanks — your feedback has been sent. If you need to follow up, contact {email}."
)
