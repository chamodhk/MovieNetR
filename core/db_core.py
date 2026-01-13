from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base_model import Base 

DB_URL = "sqlite:///db/output.db"
DB_URL2 = "sqlite:///db/experiment.db"



def get_db_session():
    engine = create_engine(DB_URL, future= True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()
    return session

def get_db_session2():
    engine2 = create_engine(DB_URL2, future=True)
    Session2 = sessionmaker(bind = engine2 )
    session2 = Session2()
    return session2
