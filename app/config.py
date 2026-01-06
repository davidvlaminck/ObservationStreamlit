from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration.

    Phase 0 keeps this intentionally small.

    Configuration precedence (highest to lowest):
    - Environment variables
    - Streamlit secrets (later, when we wire `st.secrets`)
    - Defaults
    """

    app_name: str = "Observation Streamlit"
    environment: str = "dev"  # dev|prod


def load_config() -> AppConfig:
    env = os.environ.get("APP_ENV", "dev").strip() or "dev"
    name = os.environ.get("APP_NAME", "Observation Streamlit").strip() or "Observation Streamlit"
    return AppConfig(app_name=name, environment=env)

