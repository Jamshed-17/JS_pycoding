from sqlalchemy import Integer, Column, String, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Session
import sqlalchemy


engine = sqlalchemy.create_engine("sqlite:///data/DataBase.db")

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    complite_tasks = Column(Text)
    admin = Column(Boolean, default=False)
    page_number = Column(Integer)

Base.metadata.create_all(bind=engine)


