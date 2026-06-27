from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load the .env file into the OS environment FIRST, so that os.getenv() below
# can see the non-prefixed values (LLM_BASE_URL, LLM_API_KEY).
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIDEKICK_",
        env_file=".env",
        extra="ignore",
    )

    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_api_key: str = ""
    triage_model: str = "gemini-2.5-flash-lite"
    act_model: str = "gemini-2.5-flash"

    tick_seconds: int = 60
    data_dir: Path = Path("./data")
    fact_dedup_distance: float = 0.15

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import os
        if not self.llm_api_key:
            self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_base_url = os.getenv("LLM_BASE_URL", self.llm_base_url)
        self.data_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()