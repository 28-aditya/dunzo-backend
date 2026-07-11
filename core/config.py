import os
from dotenv import load_dotenv

load_dotenv()

COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")

RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "5/minute")
RATE_LIMIT_REFRESH = os.getenv("RATE_LIMIT_REFRESH", "30/minute")

# Shared cookie attributes for set/delete consistency.
COOKIE_KWARGS = {
    "httponly": True,
    "samesite": "none",
    "secure": True,
    "domain": COOKIE_DOMAIN,
}


def validate_env() -> None:
    missing = [
        name for name in ("JWT_SECRET", "DATABASE_URL")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
