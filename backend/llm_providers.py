import logging

from .config import Config
from .rate_limiter import check_rate_limit

logger = logging.getLogger(__name__)


# Commented out on 2026-09-18, not deleted — Mistral Large is blocked with a
# 403 tier_not_allowed on our current account, and Mistral Small is returning
# a cold 429 on every single request regardless of spacing (confirmed via a
# spaced-out test, not a burst issue). Root cause looked like the account's
# "API pay-as-you-go" toggle being off, but that's unconfirmed and we're
# routing around it for now rather than chasing it further. Re-enable by
# uncommenting _build_mistral / _build_mistral_small and their two blocks in
# get_llms below, once the account side is sorted.
#
# def _build_mistral():
#     from langchain_openai import ChatOpenAI
#
#     if not Config.MISTRAL_API_KEY:
#         logger.debug("MISTRAL_API_KEY not set — skipping Mistral in fallback chain.")
#         return None
#
#     return ChatOpenAI(
#         model="mistral-large-latest",
#         api_key=Config.MISTRAL_API_KEY,
#         base_url="https://api.mistral.ai/v1",
#         max_retries=0,
#         max_tokens=8000,
#         timeout=90,
#     )
#
#
# def _build_mistral_small():
#     from langchain_openai import ChatOpenAI
#
#     if not Config.MISTRAL_API_KEY:
#         logger.debug("MISTRAL_API_KEY not set — skipping Mistral Small in fallback chain.")
#         return None
#
#     return ChatOpenAI(
#         model="mistral-small-latest",
#         api_key=Config.MISTRAL_API_KEY,
#         base_url="https://api.mistral.ai/v1",
#         max_retries=0,
#         max_tokens=8000,
#         timeout=60,
#     )


def _build_deepseek():
    from langchain_openai import ChatOpenAI

    if not Config.DEEPSEEK_API_KEY:
        logger.debug("DEEPSEEK_API_KEY not set — skipping DeepSeek in fallback chain.")
        return None

    return ChatOpenAI(
        model="deepseek-chat",
        api_key=Config.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        max_retries=0,
        max_tokens=8000,
        timeout=90,
    )


def _build_gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI

    if not Config.GEMINI_API_KEY:
        logger.debug("GEMINI_API_KEY not set — skipping Gemini in fallback chain.")
        return None

    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=Config.GEMINI_API_KEY,
        max_retries=0,
        max_output_tokens=5000,
        timeout=30,
    )


def _build_gemini_flash_31():
    from langchain_google_genai import ChatGoogleGenerativeAI

    if not Config.GEMINI_API_KEY:
        logger.debug("GEMINI_API_KEY not set — skipping Gemini 3.1 Flash in fallback chain.")
        return None

    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash",
        google_api_key=Config.GEMINI_API_KEY,
        max_retries=0,
        max_output_tokens=5000,
        timeout=30,
    )


def _within_provider_limits(name: str, rpm: int, rpd: int) -> bool:
    """Checks a provider's self-imposed RPM and RPD budgets before we
    attempt to use it. An rpm/rpd of 0 means "no self-imposed limit" —
    the intended state once a provider is on a paid tier with enough
    headroom that self-throttling is no longer needed.
    """
    if rpm and not check_rate_limit(f"llm:{name}:rpm", window_seconds=60, max_requests=rpm):
        logger.info("%s at self-imposed RPM limit (%d/min) — skipping for this attempt.", name, rpm)
        return False
    if rpd and not check_rate_limit(f"llm:{name}:rpd", window_seconds=86400, max_requests=rpd):
        logger.info("%s at self-imposed RPD limit (%d/day) — skipping for this attempt.", name, rpd)
        return False
    return True


def get_llms(prefer: str = "scheme"):
    """Build the ordered LLM fallback chain, skipping any provider that's
    currently at its own self-imposed rate limit (see Config.*_RPM/_RPD).

    Chain order: DeepSeek -> Gemini 3.5 Flash -> Gemini 3.1 Flash.

    Mistral (Large and Small) is commented out above, not deleted — see the
    note at the top of the file for why. Re-add to this chain once that's
    resolved.

    Gemini 3.1 Flash added 2026-09-18 as a second, independent Gemini model
    alongside 3.5 Flash, so a single model's transient 503 (seen from Google
    during testing) doesn't take out the whole chain in one hit. Whether the
    two models share one account-level Gemini quota or have separate pools
    is UNCONFIRMED — same caveat as the old Mistral Small note. GEMINI_31_RPM
    / GEMINI_31_RPD default to 0 (unlimited) until that's actually tested.

    DeepSeek added 2026-09-18 as the new primary — genuinely free tier,
    reliable function calling on its chat endpoint. Note: requests route
    through DeepSeek's servers in mainland China, so expect somewhat higher
    latency than Mistral/Gemini; keep an eye on this in production.

    Groq is intentionally excluded: llama-3.3-70b-versatile was deprecated
    Aug 16, 2026, and its replacement (openai/gpt-oss-120b) has a confirmed
    open LangChain bug (langchain-ai/langchain#34155) making it incompatible
    with create_agent's tools + response_format combination. Re-add Groq
    here if that's ever resolved upstream.

    SambaNova was tried as a second fallback (Aug 2026) but the account had
    no funded balance and was dropped rather than left as dead weight in
    the chain. Re-add if there's a funded account.
    """
    candidates = []

    deepseek = _build_deepseek()
    if deepseek is not None and _within_provider_limits("deepseek", Config.DEEPSEEK_RPM, Config.DEEPSEEK_RPD):
        candidates.append(deepseek)

    gemini = _build_gemini()
    if gemini is not None and _within_provider_limits("gemini", Config.GEMINI_RPM, Config.GEMINI_RPD):
        candidates.append(gemini)

    gemini_31 = _build_gemini_flash_31()
    if gemini_31 is not None and _within_provider_limits("gemini_31", Config.GEMINI_31_RPM, Config.GEMINI_31_RPD):
        candidates.append(gemini_31)

    return candidates