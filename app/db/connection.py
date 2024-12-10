from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@localhost:3306/tg_proxy"  # default value
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # enables connection pool "pre-ping" feature
    pool_recycle=3600,   # recycle connections after 1 hour
)


DBSession = sessionmaker(bind=engine)

def get_session():
    return DBSession()