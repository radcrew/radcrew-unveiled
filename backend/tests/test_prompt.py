from app.chat.prompt import build_chat_prompt
from app.models import KnowledgeChunk


def test_build_chat_prompt_joins_sources_and_question():
    chunks = [
        KnowledgeChunk(
            id="a:0",
            title="About",
            text="We build things.",
            tokens=["we", "build"],
        ),
        KnowledgeChunk(
            id="b:0",
            title="Contact",
            text="Email us.",
            tokens=["email", "us"],
        ),
    ]
    out = build_chat_prompt("What do you do?", chunks, history=None)
    assert "You are RadCrew's website assistant." in out
    assert "Source 1 (About): We build things." in out
    assert "Source 2 (Contact): Email us." in out
    assert "Question: What do you do?" in out
    assert "Format the answer in simple Markdown for readability" in out


def test_build_chat_prompt_no_context_falls_back_to_placeholder():
    out = build_chat_prompt("Hello?", [], history=None)
    assert "Context sources:" in out
    assert "No context found." in out
