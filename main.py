from fastapi import FastAPI, Depends, HTTPException
import logging
from database import Base, engine
from model.users import User
from model.exercise import exercise
from model.workout import workout
from model.workout_exercise import workout_exercise

from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserSignup, UserLogin, CreateWorkout, WorkoutUpdate, CreateWorkoutExercise, WorkoutExerciseUpdate, CreateExercise, ExerciseUpdate, WorkoutExerciseCreate
from core.security import hash_password, verify_password, create_access_token
from core.auth import get_current_user
from core.rate_limiter import rateLimiter

app = FastAPI()
logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)

login_limiter = rateLimiter(
    max_attempts=5,
    window_seconds=60
)

@app.get("/")
def home():
    logger.info("GET method called on / endpoint")
    return "FastAPI Workout Tracker API"

# @app.get("/test_Database")
# def test_database():

#     try:
#         with engine.connect():
#             return "database connection successfull"

#     except Exception as error:
#         return {
#             "message": "database connection failed",
#             "error": str(error)
#         }
@app.post("/users/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    logger.info("new user registration")
    new_user = User(
        name = user.name,
        age = user.age,
        weight = user.weight,
        password_hash = hash_password(user.password),
        role = "User"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)    # adds a new user id for any user added

    return {
        "message": "New user added!",
        "user id assigned": new_user.id
    }

@app.post("/users/login")
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    # rate limiter logic implementation
    if not login_limiter.is_allowed(user.name):
        raise HTTPException(status_code=429, detail="too many login attempts, try again later")
    
    logger.info("existing user login")
    db_user = db.query(User).filter(User.name == user.name).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="invalid username or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="invalid username or password")

    # create an access token for the time period of the password to start
    access_token = create_access_token(db_user.id)

# bearer tells jwt is the authentication credentials used to access the api, and the token is the access token generated for the user 
    logger.info("user login successful")
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/users/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "age": current_user.age,
        "weight": current_user.weight
    }

# allowing users to add their scheduled workouts to the database
@app.post("/workouts")
def create_workout(workout_data: CreateWorkout, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_workout = workout(
        user_id = current_user,
        name = workout_data.name,
        scheduled_at = workout_data.scheduled_at,
        workout_comment = workout_data.comments
        )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return{
        "message" : "workout created successfully",
        "workout_id" : new_workout.id,
        "workout_name" : new_workout.name
    }

# allowing users to display the workouts added
@app.get("/workouts")
def get_workout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workouts = db.query(workout).filter(workout.user_id == current_user.user_id).all()

    return workouts

# allowing users to update their workouts
@app.put("/workouts/{workout_id}")
def update_workout(workout_id: int, workout_data: WorkoutUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout :
        raise HTTPException(
            status_code=404, 
            detail="workout not found"
        )

    if workout_data.name is not None:
        existing_workout.name = workout_data.name

    if workout_data.scheduled_at is not None:
        existing_workout.scheduled_at = workout_data.scheduled_at

    if workout_data.comments is not None:
        existing_workout.comments = workout_data.comments

    if workout_data.status is not None:
        existing_workout.status = workout_data.status

    db.commit()
    db.refresh(existing_workout)

    return {
        "message": "Workout updated successfully",
        "workout_id": existing_workout.id,
        "workout_name": existing_workout.name
    }

# allowing users to delete the existing workout
@app.delete("workout/{workout_id}")
def delete_workout(workout_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="workout not found"
        )

    db.delete(existing_workout)
    db.commit()

    return{
        "message": "workout deleted"
    }

@app.post("workout/{workout_id}/exercise")
def add_exercise_to_workout(workout_id: int, exercise_data: CreateWorkoutExercise, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="workout not found"
        )

    new_workout_exercise = workout_exercise(
        workout_id = workout_id,
        exercise_id = exercise_data.exercise_id,
        sets = exercise_data.sets,
        repetition = exercise_data.repetition,
        weight = exercise_data.weight
    )

    db.add(new_workout_exercise)
    db.commit()
    db.refresh(new_workout_exercise)

    return{
        "message": "exercise added to workout",
        "workout_exercise_id": new_workout_exercise.id
    }

# to exercise specific to a workout
@app.get("workout/{workout_id}/exercise")
def get_workout_exercises(workout_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="workout not found"
        )

    exercise = db.query(workout_exercise).filter(workout_exercise == workout_id).all()

    return exercise

# update the workout exercises
@app.post("workout/{workout_id}/exercise")
def update_workout(workout_exercise_id: int, exercise_data: WorkoutExerciseUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_exercise = db.query(workout_exercise).filter(workout_exercise.id == workout_exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="workout exercise not found"
        )

    existing_workout = db.query(workout).filter(workout_exercise.id == workout_exercise_id).first()

    if not existing_workout:
            raise HTTPException(
            status_code=404,
            detail="workout not found"
        )

    if exercise_data.sets is not None:
        existing_exercise.sets = exercise_data.sets

    if exercise_data.repetition is not None:
        existing_exercise.repetition = exercise_data.repetition

    if exercise_data.weight is not None:
        existing_exercise.weight = exercise_data.weight

    db.commit()
    db.refresh(existing_workout)

    return{
        "message": "workout exercise updated"
    }

# allowing users to delete workout exercises
@app.delete("/workout/{workout_id}/exercise")
def delete_workout(workout_exercise_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_exercise = db.query(workout_exercise).filter(workout_exercise.id == workout_exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="workout exercise not found"
        )

    db.delete(existing_exercise)
    db.commit()

    return{
        "message": "workout deleted"
    }   

# allowing users to add, update and delete exercises
@app.post("/exercise")
def create_exercise(exercise_data: CreateExercise, db: Session = Depends(get_db)):
    new_exercise = exercise(
        name = exercise_data.name, 
        description = exercise_data.description,
        category = exercise_data.category)

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return{
        "message": "exercise added successfully",
        "exercise_id": new_exercise.id
    }

# read all exercises
@app.get("/exercise")
def get_all_exercises(db: Session = Depends(get_db)):
    return db.query(exercise).all

# read all exerices
@app.get("/exercise/{exercise_id}")
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    existing_exercise = db.query(exercise).filter(exercise.id == exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404, 
            detail= "exercise not found"
        )

    return existing_exercise

#update exercise
@app.put("/exercises/{exercise_id}")
def update_exercise(exercise_id: int, exercise_data: ExerciseUpdate, db: Session = Depends(get_db)):
    existing_exercise = db.query(exercise).filter(exercise.id == exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )

    if exercise_data.name is not None:
        existing_exercise.name = exercise_data.name

    if exercise_data.description is not None:
        existing_exercise.description = exercise_data.description

    if exercise_data.category is not None:
        existing_exercise.category = exercise_data.category

    db.commit()
    db.refresh(existing_exercise)

    return {
        "message": "Exercise updated successfully",
        "exercise_id": existing_exercise.id
    }

# delete an exercise:
@app.delete("/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    existing_exercise = db.query(exercise).filter(exercise.id == exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )

    db.delete(existing_exercise)
    db.commit()

    return {
        "message": "Exercise deleted successfully"
    }

# exercises based on workout
@app.post("/workouts/{workout_id}/exercises")
def add_exercise_to_workout(workout_id: int, exercise_data: WorkoutExerciseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )

    existing_exercise = db.query(exercise).filter(exercise.id == exercise_data.exercise_id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )

    new_workout_exercise = workout_exercise(
        workout_id=workout_id,
        exercise_id=exercise_data.exercise_id,
        sets=exercise_data.sets,
        repetitions=exercise_data.repetitions,
        weight=exercise_data.weight
    )

    db.add(new_workout_exercise)
    db.commit()
    db.refresh(new_workout_exercise)

    return {
        "message": "Exercise added to workout successfully",
        "workout_exercise_id": new_workout_exercise.id
    }

# get exercises based on the specific workout
@app.get("/workouts/{workout_id}/exercises")
def get_workout_exercises(workout_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )

    workout_exercises_list = db.query(workout_exercise).filter(workout_exercise.workout_id == workout_id).all()
    return workout_exercises_list

@app.put("/workouts/{workout_id}/exercises/{workout_exercise_id}")
def update_workout_exercise(workout_id: int, workout_exercise_id: int, exercise_data: WorkoutExerciseUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_exercise = db.query(workout_exercise).join(workout, workout.id == workout_exercise.workout_id).filter(workout_exercise.id == workout_exercise_id, workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_exercise:
        raise HTTPException(
            status_code=404,
            detail="Workout exercise not found"
        )

    if exercise_data.sets is not None:
        existing_exercise.sets = exercise_data.sets

    if exercise_data.repetitions is not None:
        existing_exercise.repetitions = exercise_data.repetitions

    if exercise_data.weight is not None:
        existing_exercise.weight = exercise_data.weight

    db.commit()
    db.refresh(existing_exercise)

    return {
        "message": "Workout exercise updated successfully",
        "workout_exercise_id": existing_exercise.id
    }

# to create an endpoint to get pending/active workout status for workout
@app.get("/workouts/pending")
def get_pending_workouts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workouts = db.query(workout).filter(workout.user_id == current_user.id, workout.status == "pending").order_by(workout.scheduled_at.asc()).all()

    return workouts

# to update the workout as complete
@app.put("/workouts/{workout_id}/complete")
def complete_workout(workout_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    existing_workout = db.query(workout).filter(workout.id == workout_id, workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )

    existing_workout.status = "completed"

    db.commit()
    db.refresh(existing_workout)

    return {
        "message": "Workout marked as completed",
        "workout_id": existing_workout.id,
        "status": existing_workout.status
    }

# to show the workout history of users
@app.get("/workouts/history")
def get_workout_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed_workouts = db.query(workout).filter(workout.user_id == current_user.id, workout.status == "completed").order_by(workout.scheduled_at.desc()).all()

    return completed_workouts

# workout progress and details
@app.get("/workouts/{workout_id}/report")
def get_workout_report(workout_id: int, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    
    existing_workout = db.query(workout).filter(workout.id == workout_id,workout.user_id == current_user.id).first()

    if not existing_workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )

    exercises = db.query(workout_exercise).filter(workout_exercise.workout_id == workout_id).all()

    return {
        "workout_id": existing_workout.id,
        "workout_name": existing_workout.name,
        "scheduled_at": existing_workout.scheduled_at,
        "status": existing_workout.status,
        "comments": existing_workout.comments,
        "exercises": [
            {
                "exercise_id": item.exercise_id,
                "sets": item.sets,
                "repetitions": item.repetitions,
                "weight": item.weight
            }
            for item in exercises
        ]
    }

#progress report across multiple workouts
@app.get("/progress/{exercise_id}")
def get_exercise_progress(exercise_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    progress = (
        db.query(workout_exercise)
        .join(
            workout,
            workout.id == workout_exercise.workout_id
        )
        .filter(
            workout_exercise.exercise_id == exercise_id,
            workout.user_id == current_user.id,
            workout.status == "completed"
        )
        .order_by(
            workout.scheduled_at.asc()
        )
        .all()
    )

    return [
        {
            "workout_id": item.workout_id,
            "scheduled_at": item.workout.scheduled_at,
            "sets": item.sets,
            "repetitions": item.repetitions,
            "weight": item.weight
        }
        for item in progress
    ]