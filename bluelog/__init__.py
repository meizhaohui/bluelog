#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/16 20:51
@File    : views.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description:  构造文件
"""
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.commands import register_commands
from bluelog.extensions import bootstrap, db, moment, ckeditor, mail, \
    login_manager, csrf
from bluelog.models import Admin, Category, Post, Comment
from bluelog.settings import config


def create_app(config_name='default'):
    # 初始化app函数
    app = Flask('bluelog')
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_shell_commands(app)
    register_template_context(app)
    register_errors(app)

    return app


# 注册日志
def register_logging(app):
    """注册日志"""

    # 在日志中加入请求信息
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '%(asctime)s IP:%(remote_addr)s %(url)s %(threadName)s filename: %(filename)s line:%(lineno)s %(levelname)s:  %(message)s'
    )
    # 设置日志记录器等级
    app.logger.setLevel(logging.INFO)
    # formatter = logging.Formatter(
    #     '%(asctime)s %(threadName)s filename: %(filename)s line:%(lineno)s %(levelname)s:  %(message)s'
    # )
    file_handler = RotatingFileHandler(
        os.getenv('LOGGING_FILE'),
        maxBytes=104857600,  # 100MB,  104857600=100 * 1024 * 1024
        backupCount=10  # 10个备份文件
    )
    # file_handler.setFormatter(formatter)
    file_handler.setFormatter(request_formatter)
    file_handler.setLevel(logging.INFO)

    # 注册邮件日志处理器
    mail_handler = SMTPHandler(
        mailhost=os.getenv('MAIL_SERVER'),
        fromaddr=os.getenv('MAIL_USERNAME'),
        toaddrs=os.getenv('BLUELOG_ADMIN_EMAIL'),
        subject='Application Error',
        credentials=(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    # if not app.debug:
    #     app.logger.addHandler(file_handler)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(mail_handler)


# 注册命令行工具
def register_shell_commands(app):
    return register_commands(app)


# 注册扩展
def register_extensions(app):
    # 初始化扩展
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # 注册CSRF保护扩展
    register_filter(app)  # 注册自定义过滤器


# 注册蓝图
def register_blueprints(app):
    # 注册蓝图, url_prefix指定url前缀
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')


# 注册模板上下文
def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        # if current_user.is_authenticated:
        #     # 获取未回复的评论数
        #     unread_comments = Comment.query.filter_by(reviewed=False).count()
        # else:
        #     unread_comments = None
        unread_comments = Comment.query.filter_by(reviewed=False).count()
        return dict(admin=admin,
                    categories=categories,
                    unread_comments=unread_comments)


# 注册错误处理
def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return render_template('errors/400.html',
                               description=e.description), 400


def register_filter(app):
    """自定义过滤器"""
    @app.template_filter('searchword')
    def searchword(data, key_word):
        if data.find(key_word) == -1:
            data = data + '...<span class="redfont">' + key_word + '...</span>'
        else:
            data = data.replace(key_word, '<span class="redfont">' + key_word + '</span> ')
        return data