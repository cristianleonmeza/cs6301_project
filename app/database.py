from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

UsersBase = declarative_base()
InventoryBase = declarative_base()

users_engine = create_engine(settings.users_db_url, connect_args={"check_same_thread": False})
inventory_engine = create_engine(settings.inventory_db_url, connect_args={"check_same_thread": False})

UsersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=users_engine)
InventorySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=inventory_engine)


def get_users_db():
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_inventory_db():
    db = InventorySessionLocal()
    try:
        yield db
    finally:
        db.close()