from pydantic import BaseModel


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

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int
    quantity: int