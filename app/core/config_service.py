from functools import lru_cache
from pydantic import BaseModel


# Using BaseModel instead of BaseSettings due to Pydantic v2 migration
class ConfigService(BaseModel):
    APP_NAME: str = "ADHD CalendarModelSchemaSchema"
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"

    @property
    def database_url_with_args(self) -> str:
        return f"{self.database_url}?async_fallback=True"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_config() -> ConfigService:
    return ConfigService()
