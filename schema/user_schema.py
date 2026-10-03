from pydantic import BaseModel
from datetime import datetime

class UserSignup(BaseModel):
    name: str
    age: int
    weight: float
    password: str

class UserLogin(BaseModel):
    name: str
    password: str

class CreateWorkout(BaseModel):
    name: str
    scheduled_at : datetime | None = None
    comments: str | None = None

class WorkoutUpdate(BaseModel):
    name: str
    scheduled_at : datetime | None = None
    comments: str | None = None
    status: str | None = None

class CreateWorkoutExercise(BaseModel):
    exercise_id: int
    sets: int
    repetition: int
    weight: float | None = None

class WorkoutExerciseUpdate(BaseModel):
    sets: int | None = None
    repetition: int | None = None
    weight: float | None = None

class CreateExercise(BaseModel):
    name: str
    description: str | None = None
    category: str

class ExerciseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None

class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    sets: int
    repetition: int
    weight: float | None = None

class WorkoutExerciseUpdate(BaseModel):
    sets: int
    repetition: int
    weight: float | None = None


