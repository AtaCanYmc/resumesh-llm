import asyncio
import logging
import random

import httpx
from openai import APIStatusError

from resumesh_llm.core.exceptions import RateLimitError

logger = logging.getLogger(__name__)


async def retry_with_backoff(
    coro_func,
    *args,
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    **kwargs,
):
    """Retries an async function with exponential backoff and jitter."""
    import json

    from pydantic import ValidationError

    delay = initial_delay
    for attempt in range(retries + 1):
        try:
            return await coro_func(*args, **kwargs)
        except (
            RateLimitError,
            httpx.HTTPStatusError,
            httpx.RequestError,
            ValidationError,
            json.JSONDecodeError,
        ) as e:
            if attempt == retries:
                logger.error(f"Failed after {retries} retries: {str(e)}")
                raise

            sleep_time = delay + random.uniform(0, 0.5 * delay)
            logger.warning(
                f"Rate limit or network error. Retrying in {sleep_time:.2f}s... (Attempt {attempt + 1}/{retries})"
            )
            await asyncio.sleep(sleep_time)
            delay *= backoff_factor
        except APIStatusError as e:
            if e.status_code == 429:
                if attempt == retries:
                    raise RateLimitError(str(e), provider="openai") from e
                sleep_time = delay + random.uniform(0, 0.5 * delay)
                logger.warning(
                    f"API Rate Limit (429) hit. Retrying in {sleep_time:.2f}s... (Attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(sleep_time)
                delay *= backoff_factor
            else:
                if attempt == retries:
                    raise
                sleep_time = delay + random.uniform(0, 0.5 * delay)
                await asyncio.sleep(sleep_time)
                delay *= backoff_factor
