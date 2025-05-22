from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv("DB_PASSWORD")

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{os.getenv("DB_PASSWORD")}@localhost/mechanic_db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"


class ProductionConfig: 
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI" )
    CACHE_TYPE = "SimpleCache"
