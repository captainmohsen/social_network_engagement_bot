import uuid
from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class UserSession(Base):
    __tablename__ = 'user_session'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_archive = None
    session_data = Column(String(), index=True)
    is_revoked = Column(Boolean(), default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete="CASCADE"))
    user = relationship('User', back_populates='user_session')

