import httpx
import pytest
import respx

from app.config import Settings
from app.knowledge.contentful_loader import load_contentful_documents, parse_contentful_entries_json


@pytest.mark.asyncio
async def test_returns_empty_without_credentials():
    s = Settings(
        CONTENTFUL_SPACE_ID=None,
        CONTENTFUL_DELIVERY_TOKEN=None,
        CONTENTFUL_ENVIRONMENT="master",
    )
    assert await load_contentful_documents(s) == []


@pytest.mark.asyncio
@respx.mock
async def test_loads_entries_from_contentful():
    space = "spc123"
    url = f"https://cdn.contentful.com/spaces/{space}/environments/master/entries"
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {
                        "sys": {"id": "entryXYZ"},
                        "fields": {
                            "title": {"en-US": "From CMS"},
                            "body": {"en-US": "Important body text."},
                        },
                    }
                ]
            },
        )
    )

    s = Settings(
        CONTENTFUL_SPACE_ID=space,
        CONTENTFUL_DELIVERY_TOKEN="secret-token",
        CONTENTFUL_ENVIRONMENT="master",
    )
    docs = await load_contentful_documents(s)
    assert len(docs) == 1
    d = docs[0]
    assert d.id == "contentful:entryXYZ"
    assert d.title == "From CMS"
    assert "Important body text" in d.text
    assert d.url == f"https://app.contentful.com/spaces/{space}/entries/entryXYZ"


def test_parse_json_helper():
    payload = """
    {
      "items": [
        {
          "sys": { "id": "e1" },
          "fields": {
            "name": "Short",
            "heading": "",
            "extra": 42
          }
        }
      ]
    }
    """
    docs = parse_contentful_entries_json(payload, "space99")
    assert len(docs) == 1
    assert docs[0].title == "Short"
    assert docs[0].url == "https://app.contentful.com/spaces/space99/entries/e1"
