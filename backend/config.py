import os


def _split_csv(value: str):
    return [v.strip() for v in value.split(",") if v.strip()]


class Config:
    """Central place for all environment-driven configuration.

    Nothing here should read env vars directly anywhere else in the app —
    add new settings here so there's one place to check what's configurable.
    """

    # --- Server ---
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g.
    # "https://sarkarly.vercel.app,http://localhost:3000"
    # Defaults to "*" for local development convenience, but this should
    # ALWAYS be set explicitly in production.
    _raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_ORIGINS = "*" if _raw_origins == "*" else _split_csv(_raw_origins)

    # --- Logging ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


    GEMINI_RPM = int(os.getenv("GEMINI_RPM", "5"))
    GEMINI_RPD = int(os.getenv("GEMINI_RPD", "18"))
    GEMINI_31_RPM = int(os.getenv("GEMINI_31_RPM", "0"))
    GEMINI_31_RPD = int(os.getenv("GEMINI_31_RPD", "0"))
    MISTRAL_RPM = int(os.getenv("MISTRAL_RPM", "0"))
    MISTRAL_RPD = int(os.getenv("MISTRAL_RPD", "0"))
    MISTRAL_SMALL_RPM = int(os.getenv("MISTRAL_SMALL_RPM", "0"))
    MISTRAL_SMALL_RPD = int(os.getenv("MISTRAL_SMALL_RPD", "0"))
    DEEPSEEK_RPM = int(os.getenv("DEEPSEEK_RPM", "0"))
    DEEPSEEK_RPD = int(os.getenv("DEEPSEEK_RPD", "0"))

    # --- Per-user / per-IP daily request limits (Flask-Limiter) ---
    # Strings in Flask-Limiter's own format, e.g. "80 per day".
    SCHEME_MATCH_DAILY_LIMIT = os.getenv("SCHEME_MATCH_DAILY_LIMIT", "50 per day")
    SCHEME_DIRECTORY_DAILY_LIMIT = os.getenv("SCHEME_DIRECTORY_DAILY_LIMIT", "50 per day")
    SCHEME_DETAILS_DAILY_LIMIT = os.getenv("SCHEME_DETAILS_DAILY_LIMIT", "20 per day")
    LEGAL_ADVISORY_DAILY_LIMIT = os.getenv("LEGAL_ADVISORY_DAILY_LIMIT", "20 per day")

    @classmethod
    def has_any_llm_key(cls) -> bool:
        return bool(cls.MISTRAL_API_KEY or cls.GEMINI_API_KEY or cls.DEEPSEEK_API_KEY)