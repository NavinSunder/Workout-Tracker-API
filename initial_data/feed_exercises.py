from database import SessionLocal
from model.exercise import exercise


class exerciseSeeder:

    def __init__(self):
        self.db = SessionLocal()

    def seed(self):

        exercises = [
            exercise(
                name="Bench Press",
                description="A strength exercise that targets the chest",
                category="Strength"
            ),

            exercise(
                name="Squat",
                description="A lower body strength exercise",
                category="Strength"
            ),

            exercise(
                name="Deadlift",
                description="A compound exercise targeting the back and legs",
                category="Strength"
            ),

            exercise(
                name="Push Up",
                description="A bodyweight exercise targeting the chest",
                category="Strength"
            ),

            exercise(
                name="Pull Up",
                description="A bodyweight exercise targeting the back",
                category="Strength"
            ),

            exercise(
                name="Running",
                description="A cardiovascular exercise",
                category="Cardio"
            ),

            exercise(
                name="Cycling",
                description="A cardiovascular exercise using a bicycle",
                category="Cardio"
            ),

            exercise(
                name="Plank",
                description="A core stability exercise",
                category="Strength"
            ),

            exercise(
                name="Lunges",
                description="A single-leg exercise targeting the lower body",
                category="Strength"
            ),

            exercise(
                name="Hamstring Stretch",
                description="A flexibility exercise targeting the hamstrings",
                category="Flexibility"
            )
        ]

        self.db.add_all(exercises)
        self.db.commit()

        print("Exercises seeded successfully!")

    def close(self):
        self.db.close()


if __name__ == "__main__":

    seeder = exerciseSeeder()

    try:
        seeder.seed()

    finally:
        seeder.close()