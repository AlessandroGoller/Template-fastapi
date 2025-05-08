from functools import cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    log_level: str = "INFO"

    database_url: str = "sqlite:///./test.db"

    # --------- Firebase config variables ---------
    api_key: str = ""
    auth_domain: str = ""
    project_id: str = ""
    storage_bucket: str = ""
    messaging_sender_id: str = ""
    app_id: str = ""
    measurement_id: Optional[str] = ""

    @property
    def firebase_config(self) -> dict[str, Optional[str]]:
        return {
            "apiKey": self.api_key,
            "authDomain": self.auth_domain,
            "projectId": self.project_id,
            "storageBucket": self.storage_bucket,
            "messagingSenderId": self.messaging_sender_id,
            "appId": self.app_id,
            "measurementId": self.measurement_id,
            "databaseURL": self.database_url,
        }
    # --------- End of Firebase config variables ---------

    # --------- FastAPI config variables ---------
    allow_origins_list: list[str] = ["*"]
    allow_methods_list: list[str] = ["*"]
    allow_headers_list: list[str] = ["*"]
    # --------- End of FastAPI config variables ---------

@cache
def get_config() -> Config:
    return Config()

settings = get_config()
