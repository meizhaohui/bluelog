#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/19 21:32
@File    : fakes.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 构建虚拟数据函数
"""
import random
from faker import Faker

from bluelog.models import Admin, Category, Post, Comment
from bluelog.extensions import db
from sqlalchemy.exc import IntegrityError

fake = Faker()


def fake_admin():
    """生成虚拟管理员信息"""
    admin = Admin(
        username='admin',
        blog_title='Bluglog',
        blog_sub_title="No,I'm the real thing.",
        name='meizhaohui',
        about='Enjoy your life'
    )
    # 注：当在models.py中Admin类中继承UserMixin时，此处会变黄
    # 生成虚拟数据时，可将Admin类中的UserMixin去掉
    admin.password = 'Helloflask'
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    """生成虚拟分类信息"""
    category = Category(name='default')
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    """生成虚拟文章"""
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(500),
            timestamp=fake.date_time_this_year()
        )
        post.category = Category.query.get(
            random.randint(1, Category.query.count()))
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    """生成虚拟评论"""
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.ascii_email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.ascii_email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = Comment(
            author='meizhaohui',
            email=fake.ascii_email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # 回复
    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.ascii_email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count())),
            replied=Comment.query.get(random.randint(1, Comment.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

