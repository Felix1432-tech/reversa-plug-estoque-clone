from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database (Supabase Postgres)
    database_url: str

    # Encryption
    encryption_key: str

    # Backblaze B2
    b2_key_id: str
    b2_application_key: str
    b2_bucket_name: str = "product-photos"
    b2_endpoint_url: str = "https://s3.us-west-004.backblazeb2.com"

    # Google Drive
    google_service_account_json: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
