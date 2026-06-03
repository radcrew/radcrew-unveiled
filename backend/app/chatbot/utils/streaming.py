import logging
from collections.abc import Iterator
from time import perf_counter

logger = logging.getLogger(__name__)

STREAM_TEXT_CHUNK_SIZE = 2


def get_text_chunk_stream(
    text: str, chunk_size: int = STREAM_TEXT_CHUNK_SIZE
) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]


def timed_stream(stream: Iterator[str], label: str) -> Iterator[str]:
    """Log time-to-first-token and total stream duration at INFO.

    Timing starts when the consumer begins iterating (the stream is lazy), so it
    reflects real generation latency rather than node setup.
    """
    start = perf_counter()
    first = True
    chars = 0
    for chunk in stream:
        if first:
            logger.info("[timing] %s ttft=%.3fs", label, perf_counter() - start)
            first = False
        chars += len(chunk)
        yield chunk
    logger.info(
        "[timing] %s total=%.3fs chars=%d", label, perf_counter() - start, chars
    )
