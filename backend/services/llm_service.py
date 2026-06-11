"""
Reusable async OpenRouter LLM client using the OpenAI Python SDK.

All LLM calls in the pipeline go through `call_openrouter()`.
Uses the official OpenAI SDK with base_url override as recommended
by OpenRouter docs. Handles retries with exponential backoff for
429 / timeout errors.
"""

import os
import asyncio
import time
import re

from openai import OpenAI

from backend.config import get_settings
from backend.metrics import (
    llm_request_duration,
    llm_requests_total,
    llm_tokens_used,
    llm_errors_total,
)

DEFAULT_MODEL = "anthropic/claude-3-haiku"
ANALYSIS_MODEL = "deepseek/deepseek-chat"
COMPARISON_MODEL = "google/gemini-2.5-flash"
FALLBACK_MODEL = "anthropic/claude-3-haiku"
MAX_RETRIES = 3
INITIAL_BACKOFF = 2.0  # seconds


def _get_client() -> OpenAI:
    """
    Build an OpenAI client pointed at OpenRouter.
    Reads OPENROUTER_API_KEY from environment (K8s Secret / .env).
    """
    settings = get_settings()
    api_key = os.getenv("OPENROUTER_API_KEY", settings.openrouter_api_key)
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set in environment or .env"
        )

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=60.0,
    )


async def call_openrouter(
    prompt: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4000,
    call_type: str = "analysis",
) -> str | None:
    """
    Send a prompt to OpenRouter via the OpenAI SDK and return the
    raw response text.

    Returns None only after all retries are exhausted.
    """
    settings = get_settings()

    resolved_model = (
        model
        or settings.default_model
        or DEFAULT_MODEL
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Rough token estimation: 1 token ≈ 4 characters
    estimated_tokens = len(prompt) // 4
    llm_tokens_used.labels(call_type=call_type).inc(estimated_tokens)

    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        start = time.time()
        try:
            client = _get_client()

            # The OpenAI SDK call is synchronous, so we run it in a
            # thread to keep the async event loop free.
            completion = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    extra_headers={
                        "HTTP-Referer": "http://localhost",
                        "X-OpenRouter-Title": "Competitor Intelligence Monitor",
                    },
                    model=resolved_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                ),
                timeout=90.0
            )

            duration = time.time() - start
            text = completion.choices[0].message.content

            # Record success metrics
            llm_request_duration.labels(
                call_type=call_type, model=resolved_model
            ).observe(duration)
            llm_requests_total.labels(
                call_type=call_type, status="success"
            ).inc()

            print(
                f"  [llm] OpenRouter call succeeded "
                f"(model={resolved_model}, {duration:.1f}s)"
            )

            return text

        except Exception as e:
            duration = time.time() - start
            error_str = str(e)

            # Classify the error for metrics and retry logic
            is_rate_limit = "429" in error_str or "rate" in error_str.lower()
            is_timeout = "timeout" in error_str.lower() or "timed out" in error_str.lower()
            is_exhausted = "402" in error_str or "credit" in error_str.lower()

            if is_exhausted:
                print(f"  [llm] OpenRouter credits exhausted! Aborting retries.")
                raise Exception("OpenRouter credits exhausted")

            if is_rate_limit:
                error_type = "rate_limit"
                retry_after = _parse_retry_delay(error_str)
                wait = max(retry_after, backoff)
            elif is_timeout:
                error_type = "timeout"
                wait = backoff
            elif "parse" in error_str.lower():
                error_type = "parse_error"
                wait = backoff
            else:
                error_type = "unknown"
                wait = backoff

            llm_errors_total.labels(error_type=error_type).inc()
            llm_request_duration.labels(
                call_type=call_type, model=resolved_model
            ).observe(duration)

            if attempt == MAX_RETRIES:
                llm_requests_total.labels(
                    call_type=call_type, status="error"
                ).inc()
                print(
                    f"  [llm] OpenRouter attempt {attempt} failed "
                    f"(final): {error_str[:120]}"
                )
                return None

            llm_requests_total.labels(
                call_type=call_type, status="retry"
            ).inc()
            print(
                f"  [llm] OpenRouter attempt {attempt} failed "
                f"(waiting {wait:.1f}s): {error_str[:120]}"
            )
            await asyncio.sleep(wait)
            backoff *= 2

    return None


def _parse_retry_delay(error_str: str) -> float:
    """
    Extract retry delay from OpenRouter rate-limit error message.
    Falls back to 5s if not parseable.
    """
    # Pattern: "try again in 2.52s"
    match = re.search(r"try again in ([\d.]+)s", error_str)
    if match:
        return float(match.group(1)) + 1

    # Pattern: "retry_delay { seconds: 59 }"
    match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", error_str)
    if match:
        return float(match.group(1)) + 2

    return 5.0
