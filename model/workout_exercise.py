from sqlalchemy import Column, Integer, Float, ForeignKey
from database import Base


class workout_exercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    repetitions = Column(Integer, nullable=False)
    weight = Column(Float)