import os
from dotenv import load_dotenv

load_dotenv()

class Setting():
    DATABASE_URL = os.getenv('DATABASE_URL')

setting = Setting()