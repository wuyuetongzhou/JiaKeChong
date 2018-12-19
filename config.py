import os
import redis
import mysql.connector
from flask import logging
import logging

# basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.getcwd().replace('\\', r'\\')


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@127.0.0.1:3306/beetle_web'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # redis配置
    REDIS_HOST = "127.0.0.1"  # ip
    REDIS_PORT = 6379  # port
    REDIS_DB = 6  # 用6号库
    PASSWORD = "123456"
    # 指明sesion存储到那种类型的数据库
    SESSION_TYPE = 'redis'
    # 上面的指明的数据库的实例对象
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=PASSWORD)
    # session数据需要加密
    SESSION_USE_SIGNER = True
    # 不设置永久存储
    SESSION_PERMANENT = False
    # 默认存储的有效时长 （没有调整之前默认值是timedelta(days=31)）
    PERMANENT_SESSION_LIFETIME = 86400 * 2

    # 默认日志等级
    LOG_LEVEL = DEBUG

    # FLASK_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASK_MAIL_SENDER = 'Flask Admin <13977851103@139.com>'
    # FLASK_ADMIN = os.environ.get('FLASSKY_ADMIN')
    # MAIL_SERVER = 'smtp.139.com'
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发模式下的配置"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING


config_dict = {
    'development': DevelopmentConfig,
	'testing': TestingConfig,
    'production': ProductionConfig,
}



