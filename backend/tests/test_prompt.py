from app.chat.rag.prompt import build_chat_prompt
from app.knowledge.models import KnowledgeChunk


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
            url="https://radcrew.org/contact",
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


def test_build_chat_prompt_includes_markdown_list_style_guidance():
    out = build_chat_prompt("List the team", [], history=None)
    assert "Do not use '*' bullet symbols." in out
    assert "Use '-' for list bullets" in out
    assert "Do not nest content deeper than 2 levels." in out
    assert "Do not include URLs, links, href attributes, or markdown link syntax in the final answer." in out
    assert "Answer as briefly as possible and do not add extra details unless the user explicitly asks for them." in out
    assert "For direct questions, respond with a direct sentence only" in out
    assert "GitHub markdown files for detailed profile information" in out
    assert "first line of each GitHub team markdown file" in out and "canonical team-member name" in out
