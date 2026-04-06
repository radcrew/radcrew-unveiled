from collections.abc import Iterator

STREAM_TEXT_CHUNK_SIZE = 2

def get_text_chunk_stream(
    text: str, chunk_size: int = STREAM_TEXT_CHUNK_SIZE
) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
