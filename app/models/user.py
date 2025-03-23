import uuid
from sqlalchemy import Boolean, Column, Integer, String, Enum,ForeignKey,DateTime
from sqlalchemy.orm import relationship, column_property, Session
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    username = Column(String(120), unique=True, nullable=False)
    is_active = Column(Boolean(), default=True)
    chat_id = Column(String, nullable=True)
    user_session = relationship('UserSession', back_populates='user')
    tracks = relationship('Track', back_populates='user',cascade="all, delete-orphan")

