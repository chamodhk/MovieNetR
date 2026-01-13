from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base_model import Base 

DB_URL = "sqlite:///db/output.db"


def get_db_session():
    engine = create_engine(DB_URL, future= True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session
