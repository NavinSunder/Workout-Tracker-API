from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database import Base


class workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    scheduled_at = Column(DateTime)
    comments = Column(String)
    status = Column(String, default="pending")