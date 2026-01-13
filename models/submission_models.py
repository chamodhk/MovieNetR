from sqlalchemy import Column, Integer, Text, ForeignKey
from .base_model import Base

class Submission(Base):
    __tablename__ = "submissions"
    submission_id = Column(Integer, primary_key = True, autoincrement = True)
    id = Column(Text)
    name = Column(Text)
    self_text = Column(Text)
    score = Column(Integer)
    url = Column(Text)

