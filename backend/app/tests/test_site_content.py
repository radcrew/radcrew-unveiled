from app.chatbot.knowledge.site_content import get_static_site_documents


def test_static_documents_match_expected_ids_and_titles():
    docs = get_static_site_documents()
    by_id = {d.id: d for d in docs}
    # Every site section the bot should know about is represented.
    expected_ids = {
        "hero",
        "services",
        "how-we-work",
        "stats",
        "portfolio",
        "tech-stack",
        "testimonial",
        "faq",
        "contact",
    }
    assert expected_ids <= set(by_id)
    assert by_id["hero"].title == "RadCrew overview"
    assert by_id["contact"].url == "/#contact"
    assert "code@radcrew.org" in by_id["contact"].text


def test_static_documents_cover_site_content():
    text = " ".join(d.text for d in get_static_site_documents()).lower()
    # Content that previously lived only on the frontend (static-data.ts).
    assert "cryptopets" in text  # portfolio
    assert "2 weeks" in text  # FAQ: how quickly can you start
    assert "solana" in text  # capabilities / tech stack
    assert "jordan lee" in text  # testimonial
    assert "github.com/radcrew" in text  # social/official links
