import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, Integer, Date, Time, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine, SessionLocal

class CalendarBatch(Base):
    __tablename__ = "calendar_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sport = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="DRAFT") 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("ContentItem", back_populates="batch", cascade="all, delete-orphan")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("calendar_batches.id"), nullable=True)
    sport = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)          
    category = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(255), nullable=True)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time, default=time(10, 0)) 
    status = Column(String(20), default="DRAFT")       
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("CalendarBatch", back_populates="items")

class Athlete(Base):
    __tablename__ = "athletes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    sport = Column(String(50), nullable=False)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    birth_year = Column(Integer, nullable=False)
    notable_records = Column(Text, nullable=False)
    trivia_fact = Column(Text, nullable=False)

Base.metadata.create_all(bind=engine)

def seed_athletes_if_empty():
    db = SessionLocal()
    if db.query(Athlete).count() == 0:
        seed_data = [
            Athlete(name="Ab de Villiers", sport="Cricket", birth_month=9, birth_day=1, birth_year=1984, notable_records="Fastest ODI 50, 100, and 150 in cricket history.", trivia_fact="Known as Mr. 360 for hitting shots to all corners."),
            Athlete(name="Ishant Sharma", sport="Cricket", birth_month=9, birth_day=2, birth_year=1988, notable_records="Over 300 Test wickets for India.", trivia_fact="Bowled the famous spell to Ricky Ponting in Perth 2008."),
            Athlete(name="Viktor Axelsen", sport="Badminton", birth_month=9, birth_day=4, birth_year=1994, notable_records="Two-time Olympic Gold Medalist in Men's Singles.", trivia_fact="Fluent in Mandarin Chinese."),
            Athlete(name="Bukayo Saka", sport="Football", birth_month=9, birth_day=5, birth_year=2001, notable_records="Arsenal's Player of the Season twice.", trivia_fact="Scored a hat-trick for England against North Macedonia."),
            Athlete(name="Luka Modrić", sport="Football", birth_month=9, birth_day=9, birth_year=1985, notable_records="2018 Ballon d'Or winner and 6-time UCL champion.", trivia_fact="Captained Croatia to 2018 World Cup final."),
            Athlete(name="Ronaldo Nazário", sport="Football", birth_month=9, birth_day=18, birth_year=1976, notable_records="Two-time Ballon d'Or and 2002 World Cup champion.", trivia_fact="Youngest recipient of FIFA World Player of the Year at age 20."),
            Athlete(name="Virat Kohli", sport="Cricket", birth_month=11, birth_day=5, birth_year=1988, notable_records="50 ODI centuries, most in cricket history.", trivia_fact="Player of the Tournament in 2014 & 2016 T20 World Cups."),
            Athlete(name="MS Dhoni", sport="Cricket", birth_month=7, birth_day=7, birth_year=1981, notable_records="Only captain to win all three ICC white-ball trophies.", trivia_fact="Finished the 2011 World Cup final with an iconic six."),
            Athlete(name="Cristiano Ronaldo", sport="Football", birth_month=2, birth_day=5, birth_year=1985, notable_records="All-time top goalscorer in international men's football.", trivia_fact="5-time Champions League winner."),
            Athlete(name="Lionel Messi", sport="Football", birth_month=6, birth_day=24, birth_year=1987, notable_records="8 Ballon d'Or trophies and 2022 FIFA World Cup winner.", trivia_fact="Scored 91 goals in a single calendar year (2012)."),
            Athlete(name="PV Sindhu", sport="Badminton", birth_month=7, birth_day=5, birth_year=1995, notable_records="First Indian woman to win two consecutive Olympic medals.", trivia_fact="Won World Championship gold in 2019."),
            Athlete(name="Lin Dan", sport="Badminton", birth_month=10, birth_day=14, birth_year=1983, notable_records="Completed the Super Grand Slam by age 28.", trivia_fact="Widely regarded as the greatest badminton player of all time.")
        ]
        db.add_all(seed_data)
        db.commit()
    db.close()

seed_athletes_if_empty()