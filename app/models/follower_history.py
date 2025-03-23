import uuid
from sqlalchemy import Boolean, Column, Integer, String, Enum,ForeignKey,DateTime,UUID
from sqlalchemy.orm import relationship, column_property, Session
from app.db.base_class import Base




class FollowerHistory(Base):
    __tablename__ = "follower_history"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True,default=uuid.uuid4)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"))
    follower_count = Column(Integer)

    track = relationship("Track", back_populates="follower_history",foreign_keys=[track_id])
