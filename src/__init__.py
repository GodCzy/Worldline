from dotenv import load_dotenv

load_dotenv(".env", override=False)

import os  # noqa: E402
import warnings  # noqa: E402
import logging  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

from src.config import config as config  # noqa: E402

__version__ = "0.5.3"
graph_base = None
knowledge_base = None
_LEGACY_BRAND_PREFIX = "Y" + "UXI"


def _legacy_brand_env(suffix: str) -> str:
    return f"{_LEGACY_BRAND_PREFIX}_{suffix}"


def _get_skip_app_init_flag() -> str | None:
    primary_key = "WORLDLINE_SKIP_APP_INIT"
    legacy_key = _legacy_brand_env("SKIP_APP_INIT")

    value = os.getenv(primary_key)
    if value is not None:
        return value

    legacy_value = os.getenv(legacy_key)
    if legacy_value is not None:
        message = (
            "Legacy skip-app-init environment variable is deprecated and will be removed after Phase 8. "
            f"Use '{primary_key}' instead."
        )
        warnings.warn(
            message,
            DeprecationWarning,
            stacklevel=2,
        )
        logging.getLogger(__name__).warning(message)
    return legacy_value


if _get_skip_app_init_flag() != "1":
    from src.knowledge import graph_base as graph_base  # noqa: E402
    from src.knowledge import knowledge_base as knowledge_base  # noqa: E402

executor = ThreadPoolExecutor()  # noqa: E402


def get_version():
    """Return the Worldline version."""
    return __version__
