from .connection import engine, SessionLocal, Base
from .models import *

# Initialize models
Base.metadata.create_all(bind=engine)
