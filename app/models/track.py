from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum,UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
from app.constants.enums import SocialMediaPlatform
import uuid




class Track(Base):
    __tablename__ = "tracks"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    social_media = Column(Enum(SocialMediaPlatform))
    profile_username = Column(String)
    alert_threshold = Column(Integer, default=1000)
    alert_enabled = Column(Boolean, default=True)
    last_follower_count = Column(Integer, default=0)
    follower_history = relationship("FollowerHistory", back_populates="track", cascade="all, delete-orphan")
    user = relationship("User", back_populates="tracks",foreign_keys=[user_id])
