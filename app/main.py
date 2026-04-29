from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import (
    InventoryBase,
    UsersBase,
    get_inventory_db,
    get_users_db,
    inventory_engine,
    users_engine,
)
from .security import create_access_token, decode_token, hash_password, verify_password

app = FastAPI(title="Secure Multi-DB Cloud Processing API")


@app.on_event("startup")
def startup_seed() -> None:
    UsersBase.metadata.create_all(bind=users_engine)
    InventoryBase.metadata.create_all(bind=inventory_engine)

    user_db = next(get_users_db())
    inv_db = next(get_inventory_db())
    if not user_db.query(models.User).first():
        user_db.add(models.User(username="admin", hashed_password=hash_password("admin123"), role="admin"))
        user_db.add(models.User(username="analyst", hashed_password=hash_password("analyst123"), role="reader"))
        user_db.commit()
    if not inv_db.query(models.Product).first():
        inv_db.add_all(
            [
                models.Product(name="Laptop", category="electronics", price=1200.0),
                models.Product(name="Desk", category="furniture", price=300.0),
            ]
        )
        inv_db.commit()


def get_current_user(request: Request, user_db: Session = Depends(get_users_db)) -> models.User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    payload = decode_token(auth.split(" ", 1)[1])
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = user_db.query(models.User).filter(models.User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, user_db: Session = Depends(get_users_db)):
    user = user_db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    token = create_access_token(subject=user.username, role=user.role)
    return schemas.TokenResponse(access_token=token)


@app.get("/products", response_model=list[schemas.ProductOut])
def list_products(
    _: models.User = Depends(get_current_user),
    inv_db: Session = Depends(get_inventory_db),
):
    return inv_db.query(models.Product).all()


@app.post("/orders")
def create_order(
    order: schemas.OrderCreate,
    user: models.User = Depends(get_current_user),
    inv_db: Session = Depends(get_inventory_db),
):
    product = inv_db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    inv_db.add(models.Order(user_id=user.id, product_id=order.product_id, quantity=order.quantity))
    inv_db.commit()
    return {"message": "order accepted"}


@app.get("/reports/spend")
def spend_report(
    _: models.User = Depends(get_current_user),
    inv_db: Session = Depends(get_inventory_db),
):
    rows = (
        inv_db.query(models.Order.user_id, (models.Order.quantity * models.Product.price).label("total"))
        .join(models.Product, models.Order.product_id == models.Product.id)
        .all()
    )
    totals: dict[int, float] = {}
    for user_id, total in rows:
        totals[user_id] = totals.get(user_id, 0.0) + float(total)
    return {"totals_by_user": totals}