from sqlalchemy import Column, BigInteger, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    full_name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    interests = Column(String)
    about_me = Column(Text)
    photo_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String, nullable=True)
    swipe_quota = Column(Integer, default=30)
    is_premium = Column(Boolean, default=False)
    report_count = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    from_id = Column(BigInteger)
    to_id = Column(BigInteger)
    is_match = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
  
