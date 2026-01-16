from .base_model import Base 
from sqlalchemy import Integer, Text, Column

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, autoincrement=True, primary_key=True)
    movie_name = Column(Text)
    canonical_name = Column(Text)
