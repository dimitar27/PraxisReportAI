from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    App configuration settings loaded from the environment (.env file).

    Attributes:
        database_url (str): SQLAlchemy-compatible database connection string.
        openai_api_key (str): API key used for authenticating with OpenAI.
        secret_key (str): Secret key used to sign JWT tokens.
        access_token_expire_minutes (int): Duration in minutes before JWT expiration.
        algorithm (str): Algorithm used to encode the JWT (default: HS256).
    """
    database_url: str
    openai_api_key: str
    secret_key: str
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()