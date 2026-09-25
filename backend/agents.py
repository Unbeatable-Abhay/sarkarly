import logging

from .database import (
    get_cached_scheme_by_name,
    save_scheme,
    search_cached_schemes,
)
from .llm_providers import get_llms
from .prompts import (
    DIRECTORY_SYSTEM_PROMPT,
    LEGAL_SYSTEM_PROMPT,
    SCHEME_LIST_SYSTEM_PROMPT,
    SCHEME_SYSTEM_PROMPT,
)
from .schemas import LegalResponse, SchemeListResponse, SchemeResponse
from .search_tools import make_web_search_tool

logger = logging.getLogger(__name__)


def make_agents(llm, tools):
    from langchain.agents import create_agent

    agent_scheme = create_agent(
        llm,
        tools=tools,
        system_prompt=SCHEME_SYSTEM_PROMPT,
        response_format=SchemeResponse,
    )

    agent_legal = create_agent(
        llm,
        tools=tools,
        system_prompt=LEGAL_SYSTEM_PROMPT,
        response_format=LegalResponse,
    )

    agent_directory = create_agent(
        llm,
        tools=tools,
        system_prompt=DIRECTORY_SYSTEM_PROMPT,
        response_format=SchemeResponse,
    )

    agent_scheme_list = create_agent(
        llm,
        tools=tools,
        system_prompt=SCHEME_LIST_SYSTEM_PROMPT,
        response_format=SchemeListResponse,
    )

    return agent_scheme, agent_legal, agent_directory, agent_scheme_list


def extract_structured_response(response):
    """
    Pulls the validated Pydantic object LangChain builds when response_format
    is set, and converts it to a plain dict.
    Returns None if structuring didn't happen (e.g. model doesn't support it),
    so the caller can fall back to the next model.
    """
    structured = response.get("structured_response")

    if structured is None:
        return None

    if hasattr(structured, "model_dump"):
        return structured.model_dump()

    if isinstance(structured, dict):
        return structured

    return None


def _model_name(llm) -> str:
    return getattr(llm, "model_name", getattr(llm, "model", "unknown"))


def _build_user_message(agent_type: str, user_query: str, exclude_names: list) -> str:
    """Adds exclude context to the query sent to the agent, only when relevant."""
    if agent_type not in ("directory", "list") or not exclude_names:
        return user_query

    excluded_list = ", ".join(exclude_names)
    return (
        f"{user_query}\n\n"
        f"The user has already been shown these schemes — find DIFFERENT, "
        f"additional relevant schemes, not these: {excluded_list}"
    )


def _run_live_agent(agent_type: str, user_query: str, exclude_names: list = None):
    """The live agent+search flow. agent_type is one of:
    'scheme', 'legal', 'directory' (all full-detail, unchanged),
    'list' (light preview, used by scheme_match/scheme_directory),
    'details' (full-detail for exactly one named scheme)."""
    prefer = "legal" if agent_type == "legal" else "scheme"
    llms = get_llms(prefer=prefer)

    if not llms:
        return (
            {"error": "No AI models configured. Please set DEEPSEEK_API_KEY or GEMINI_API_KEYs."},
            503,
        )

    web_search = make_web_search_tool()
    tools = [web_search]

    message_content = _build_user_message(agent_type, user_query, exclude_names or [])

    for llm in llms:
        model_name = _model_name(llm)
        try:
            agent_scheme, agent_legal, agent_directory, agent_scheme_list = make_agents(llm, tools)

            if agent_type in ("scheme", "details"):
                agent = agent_scheme
            elif agent_type == "legal":
                agent = agent_legal
            elif agent_type == "directory":
                agent = agent_directory
            else:  # "list"
                agent = agent_scheme_list

            response = agent.invoke({
                "messages": [
                    {"role": "user", "content": message_content}
                ]
            })

            logger.debug("Raw response from %s: %r", model_name, response)

            data = extract_structured_response(response)

            if data is None:
                logger.warning("No structured_response from %s, trying fallback model...", model_name)
                continue

            return data, 200

        except Exception as exc:  # noqa: BLE001 - deliberately broad: any provider failure should fall through
            logger.warning("Error using model %s: %s — trying fallback model...", model_name, exc)
            continue

    return {"error": "All AI models are currently unavailable."}, 503


def handle_request(agent_type: str, user_query: str, exclude_names: list = None):
    """Run the query through the DB cache first where applicable, falling
    back to the live agent+search chain on a cache miss.

    agent_type:
      'scheme' / 'directory' — full-detail list requests (legacy path, still
        used if the frontend calls the old endpoints directly)
      'list' — light preview list (new default for scheme_match/scheme_directory)
      'legal' — never cached, always live (see AGENTS.md)
      'details' — full detail for exactly one named scheme

    exclude_names: scheme names already shown to the user, used by
    "load more" to avoid repeating results.

    Returns a (payload, status_code) tuple.
    """
    exclude_names = exclude_names or []

    if agent_type == "list":
        data, status = _run_live_agent("list", user_query, exclude_names=exclude_names)
        return data, status

    if agent_type == "details":
        cached_scheme = get_cached_scheme_by_name(user_query)
        if cached_scheme:
            logger.info("Serving scheme details from cache for: %r", user_query)
            return cached_scheme, 200

        data, status = _run_live_agent("details", user_query, exclude_names=None)
        if status == 200 and "schemes" in data and data["schemes"]:
            scheme = data["schemes"][0]
            save_scheme(scheme)
            return scheme, 200
        return data, status

    if agent_type in ("scheme", "directory"):
        cached = search_cached_schemes(user_query, exclude_names=exclude_names)
        if cached:
            logger.info("Serving %d scheme(s) from cache for query: %r", len(cached), user_query)
            return {
                "schemes": cached,
                "disclaimer": "This information is for awareness purposes only. Please verify through official government portals before applying.",
            }, 200

        data, status = _run_live_agent(agent_type, user_query, exclude_names=exclude_names)
        if status == 200 and "schemes" in data:
            for scheme in data["schemes"]:
                save_scheme(scheme)
        return data, status

    # "legal" — always live, never cached
    return _run_live_agent(agent_type, user_query, exclude_names=None)