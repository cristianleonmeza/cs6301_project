from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    product_id: int
    quantity: int