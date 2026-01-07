class BaseConfig:
    # Shared defaults
    SECRET_KEY = "super-secret-key"   # 🔑 replace with your actual secret
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADCARE_PUBLIC_KEY = "82cfba4bb62588a9cda7"
    UPLOADCARE_SECRET_KEY = "b1b36637bd80f173fcf2"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLite for local dev
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    # In-memory SQLite for unit tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False
    # MySQL for production (PythonAnywhere or other host)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@host/dbname"

    # Extra production security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
