from pydantic import BaseModel


class Settings(BaseModel):
    users_db_url: str = "sqlite:///./users.db"
    inventory_db_url: str = "sqlite:///./inventory.db"
    jwt_secret: str = "change-this-in-prod"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 30


settings = Settings()