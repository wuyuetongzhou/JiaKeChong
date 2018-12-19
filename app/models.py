from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
    status = db.Column(db.Integer, default=1)  # 当前状态 如果为1代表在用，0代表删除或作废


# 用户表
class User(BaseModel, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "username": self.username,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "status": self.status,
        }
        return resp_dict

    @staticmethod
    def insert_user():
        u = User(username='jkc', password='123123')
        db.session.add(u)
        db.session.commit()


# 类型表
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 类型名称
    status = db.Column(db.Integer, default=1)  # 当前状态 如果为1代表在用，0代表删除或作废

    def __repr__(self):
        return self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
        }
        return resp_dict


# 产品表
class Product(BaseModel, db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 产品名称
    content = db.Column(db.Text)  # 产品介绍内容
    content_html = db.Column(db.Text)  # 产品介绍内容_网页
    image_url = db.Column(db.String(256))  # 产品图片
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 产品类型
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))

    def __repr__(self):
        return '<Product %r>' % self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "content_html": self.content_html,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "category": self.category,
            "status": self.status,
        }
        return resp_dict


# 新闻类型表
class NewsClass(db.Model):
    __tablename__ = 'newsclass'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 类型名称
    status = db.Column(db.Integer, default=1)  # 当前状态 如果为1代表在用，0代表删除或作废

    def __repr__(self):
        return self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
        }
        return resp_dict


# 新闻资讯表
class News(BaseModel, db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=True, index=True)  # 新闻标题
    class_id = db.Column(db.Integer, db.ForeignKey('newsclass.id'))  # 产品类型
    news_class = db.relationship('NewsClass', backref=db.backref('news', lazy='dynamic'))
    digest = db.Column(db.String(512))  # 新闻摘要
    content = db.Column(db.Text)  # 新闻内容
    content_html = db.Column(db.Text)  # 新闻内容_网页
    image_url = db.Column(db.String(256))  # 新闻图片

    def __repr__(self):
        return '<News %r>' % self.name

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "news_class": self.news_class,
            "digest": self.digest,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "status": self.status
        }
        return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "news_class": self.news_class,
            "digest": self.digest,
            "content": self.content,
            "content_html": self.content_html,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "status": self.status
        }
        return resp_dict


# 应用案例表
class Case(BaseModel, db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 案例名称
    content = db.Column(db.Text)  # 案例内容
    content_html = db.Column(db.Text)  # 案例内容_网页
    image_url = db.Column(db.String(256))  # 案例图片
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 案例类型
    category = db.relationship('Category', backref=db.backref('cases', lazy='dynamic'))

    def __repr__(self):
        return '<Case %r>' % self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "content_html": self.content_html,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "category": self.category,
            "status": self.status,
        }
        return resp_dict


# 公司介绍表
class Introduction(BaseModel, db.Model):
    __tablename__ = 'introductions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 名称
    content = db.Column(db.Text)  # 新闻内容
    content_html = db.Column(db.Text)  # 新闻内容_网页
    image_url = db.Column(db.String(256))  # 图片

    def __repr__(self):
        return '<Introduction %r>' % self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "content_html": self.content_html,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "status": self.status,
        }
        return resp_dict


# 解决方案表
class Solution(BaseModel, db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, index=True)  # 名称
    digest = db.Column(db.String(512))  # 简介
    content = db.Column(db.Text)  # 内容
    image_url = db.Column(db.String(256))  # 图片

    def __repr__(self):
        return '<Solution %r>' % self.name

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "digest": self.digest,
            "image_url": self.image_url,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "status": self.status,
        }
        return resp_dict