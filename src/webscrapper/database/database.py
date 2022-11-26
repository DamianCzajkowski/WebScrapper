from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from models import Base

DB_PATH = Path(__file__).parent.resolve() / "data" / "scrapper.db"


def initialize_database() -> Session:
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(engine)
    return Session(engine)
