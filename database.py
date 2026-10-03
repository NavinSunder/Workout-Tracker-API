from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from core.config import config


db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=int(config.DB_PORT),
    database=config.DB_NAME
)

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# to ensure that just a single session is created and used throughout the application
def get_db():
    db = SessionLocal()
    yield db
    db.close()