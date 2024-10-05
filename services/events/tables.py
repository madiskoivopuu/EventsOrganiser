import sql
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    mail_acc_type = Column(Integer)
    mail_acc_id = Column(String(256))
    start_date = Column(DateTime(timezone=False), nullable=True) # Always stores UTC ISO8601 datetime
    end_date = Column(DateTime(timezone=False), nullable=True) # Always stores UTC ISO8601 datetime
    country = Column(String(64))
    city = Column(String(64))
    address = Column(String(64))
    room = Column(String(64))

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))

class TagsToEvents(Base):
    __tablename__ = "tags_to_events"

    tag_id = Column(Integer, ForeignKey(Tag.__tablename__ + ".id"), primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.__tablename__ + ".id"), primary_key=True)

Base.metadata.create_all(sql.engine)