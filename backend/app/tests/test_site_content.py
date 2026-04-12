from app.chatbot.knowledge.site_content import get_static_site_documents


def test_static_documents_match_expected_ids_and_titles():
    docs = get_static_site_documents()
    assert len(docs) == 4
    by_id = {d.id: d for d in docs}
    assert by_id["hero"].title == "RadCrew overview"
    assert by_id["contact"].url == "/#contact"
    assert "code@radcrew.org" in by_id["contact"].text
