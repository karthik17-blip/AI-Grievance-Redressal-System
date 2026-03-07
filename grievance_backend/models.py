from sqlalchemy import Column, Integer, String, Float
from database import Base

class Complaint(Base):

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    tracking_id = Column(String, unique=True, index=True)

    text = Column(String)
    category = Column(String)
    urgency = Column(String)
    department = Column(String)
    similarity_score = Column(Float)
