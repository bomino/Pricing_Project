import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_uri():
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return database_url
        return f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
