class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
    VERSION = ''

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    VERSION = 'Production'

class DevelopmentConfig(Config):
    DATABASE_URI = 'mysql://root:password@localhost/graphserver_staging'
    DEBUG = True
    SECRET_KEY = 'developmentkey'
    USERNAME = 'admin'
    PASSWORD = 'default'
    VERSION = 'Staging'
