#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/17 8:48
@File    : models.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 数据库模型
"""

from datetime import datetime
from bluelog.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 管理员模型
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 登陆用户名
    password_hash = db.Column(db.String(128))  # 密码散列值
    blog_title = db.Column(db.String(60))  # 博客标题
    blog_sub_title = db.Column(db.String(100))  # 博客副标题
    name = db.Column(db.String(30))  # 用户姓名
    about = db.Column(db.Text)  # 关于信息

    @property
    def password(self):
        raise AttributeError('禁止访问password属性!')

    @password.setter
    def password(self, password):
        """生成哈希字符串，取代set_password方法"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)


# 分类模型
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)  # 分类名称不能重复
    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


# 文章模型
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))  # 文章标题
    body = db.Column(db.Text)  # 正文
    # 使用格林威治时间，不带时区
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 是否可以评论
    can_comment = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')
    # 建立双向关系（一post对多comments），并设置级联删除，当文章删除时，相应的评论也删除掉
    comments = db.relationship('Comment', back_populates='post',
                               cascade='all,delete-orphan')


# 文章评论
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))  # 评论作者
    email = db.Column(db.String(254))  # 评论人电子邮箱
    site = db.Column(db.String(254))  # 站点
    body = db.Column(db.Text)  # 评论信息
    from_admin = db.Column(db.Boolean, default=False)  # 是否来着管理员的评论
    reviewed = db.Column(db.Boolean, default=False)  # 是否通过管理员评审
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')
    # 评论回复功能设置，评论回复理论上也算做一个评论，一个评论可以有多个回复
    # 因此可以设置表内的一对多关系
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 通过Comment对象实例的replied可以获得回复对应的原始 评论
    replied = db.relationship('Comment', back_populates='replies',
                              remote_side=[id])
    # 通过Comment对象实例的replies可以获得所有的回复
    replies = db.relationship('Comment', back_populates='replied',
                              cascade='all')
