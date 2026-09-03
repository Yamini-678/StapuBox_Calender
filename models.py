import uuid
from datetime import datetime , time
from sqlalchemy import Column , Integer , String , Date , Time ,Text, JSON, DateTime,ForeignKey
from database import Base , engine

class CalenderBatch(Base):
    __tablename__ = "calendar_batches"

    id = Column(String(36), primary_key=True, default= lambda:str(uuid.uuid4()))
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(String(36), primary_key=True, default= lambda:str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("calendar_batches.id"), nullable=True)
    sport = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(50), nullable=True)
    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    status = Column(String(20), nullable=False, default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)
    
    