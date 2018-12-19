from flask import Flask, g, render_template, request, current_app
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config_dict
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_session import Session
from logging.handlers import RotatingFileHandler
import logging
from qiniu import Auth
from app.utils.image_storage import qiniu_image_store
from app import constants


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_name):
    create_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    csrf.init_app(app)

    # 开启csrf保护
    @app.after_request
    def after_rquest(response):
        # 调用函数生成 csrf_token
        csrf_token = generate_csrf()
        # 通过 cookie 将值传给前端
        response.set_cookie('csrf_token', csrf_token)
        return response

    Session(app)

    # 注册蓝本
    from .front import front_bp
    app.register_blueprint(front_bp)
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app


def create_log(config_name):
    """记录日志的配置函数"""
    # 设置日志的记录等级
    # config_dict[config_name].LOG_LEVEL 获取开发环境日志级别
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # print(file_log_handler.BaseRotatingHandler.logging.FileHandler.baseFilename)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    # INFO manage.py 18 错误信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

