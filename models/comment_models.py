from sqlalchemy import Column, Integer, Text
from .base_model import Base

class Comment(Base):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key = True, autoincrement = True)
    parent_id = Column(Text)
    body = Column(Text)
    score = Column(Integer)
