import os

from dotenv import load_dotenv


load_dotenv()


def require_env(*names: str) -> dict[str, str]:
    """Return required environment values or report all missing names."""
    missing = [name for name in names if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            f"{', '.join(missing)}. Set them in the environment or in .env."
        )

    return {name: os.environ[name] for name in names}
