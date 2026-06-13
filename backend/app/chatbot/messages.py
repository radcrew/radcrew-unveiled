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

# Stable phrase used to recognise our own confirmation prompt in chat history.
MSG_FEEDBACK_CONFIRM_MARKER = "Should I forward it to the team?"
MSG_FEEDBACK_CONFIRM = (
    "It sounds like you want to send this message to the RadCrew team:\n\n"
    "“{body}”\n\n"
    + MSG_FEEDBACK_CONFIRM_MARKER
    + ' Reply "yes" to send or "no" to cancel.'
)
MSG_FEEDBACK_CANCELLED = (
    "No problem — I won't send that. Is there anything else I can help you with?"
)
