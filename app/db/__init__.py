from .connection import engine, get_session
from .base import Base
from .models import *

# Initialize models
Base.metadata.create_all(bind=engine)
