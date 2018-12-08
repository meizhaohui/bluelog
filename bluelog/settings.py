#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/16 21:03
@File    : settings.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 配置文件
"""

import datetime
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


class Config(object):
    SECRET_KEY = os.urandom(24)

    # 数据库配置
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/bluelog?charset=utf8mb4'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不发送警告通知
    SQLALCHEMY_ECHO = True  # 显示执行SQL

    # bootstrap设置
    BOOTSTRAP_SERVE_LOCAL = True  # 使用本地资源

    # 邮箱设置
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # 邮箱地址
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # 邮箱密码或授权码
    # 默认发件人
    MAIL_DEFAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)

    # 登陆用户cookie保存时间, 保存30天
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)

    # 管理员邮箱设置, 注意后面需要开启post.html中的发送邮件通知的代码
    BLUELOG_ADMIN_EMAIL = os.getenv('BLUELOG_ADMIN_EMAIL')

    # 主题样式设置，多种样式，默认使用Perfect Blue样式
    BLUELOG_THEMES = {'perfect_blue': 'Perfect Blue',
                      'black_swan': 'Black Swan',
                      'cerulean': 'Cerulean',
                      'cosmo': 'Cosmo',
                      'cyborg': 'Cyborg',
                      'darkly': 'Darkly',
                      'flatly': 'Flatly',
                      'journal': 'Journal',
                      'litera': 'Litera',
                      'lumen': 'Lumen',
                      'lux': 'Lux',
                      'materia': 'Materia',
                      'minty': 'Minty',
                      'pulse': 'Pulse',
                      'sandstone': 'Sandstone',
                      'simplex': 'Simplex',
                      'sketchy': 'Sketchy',
                      'slate': 'Slate',
                      'solar': 'Solar',
                      'spacelab': 'Spacelab',
                      'superhero': 'Superhero',
                      'united': 'United',
                      'yeti': 'Yeti',
                      }

    # 页数设置
    BLUELOG_POST_PER_PAGE = int(os.getenv('BLUELOG_POST_PER_PAGE'))
    BLUELOG_COMMENT_PER_PAGE = int(os.getenv('BLUELOG_COMMENT_PER_PAGE'))
    BLUELOG_MANAGE_POST_PER_PAGE = int(
        os.getenv('BLUELOG_MANAGE_POST_PER_PAGE'))
    BLUELOG_MANAGE_COMMENT_PER_PAGE = int(
        os.getenv('BLUELOG_MANAGE_COMMENT_PER_PAGE'))
    BLUELOG_MANAGE_CATEGORY_PER_PAGE = int(
        os.getenv('BLUELOG_MANAGE_CATEGORY_PER_PAGE'))

    # CKEditor富文本设置
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload'  # 处理上传文件的视图函数
    # 用户上传的文件存放的目录
    UPLOADED_PATH = os.path.join(BASE_DIR, 'static/uploads')
    CKEDITOR_ENABLE_CSRF = True  # 设置csrf保护
    CKEDITOR_ENABLE_CODESNIPPET = True  # 设置代码高亮
    CKEDITOR_CODE_THEME = 'monokai_sublime'  # 代码高亮主题,使用默认主题


# 开发环境
class DevelopmentConfig(Config):
    FLASK_DEBUG = True


# 测试环境
class TestingConfig(Config):
    FLASK_DEBUG = True


# 生产环境
class ProductionConfig(Config):
    FLASK_DEBUG = False
    SQLALCHEMY_ECHO = False  # 不显示执行SQL


# 使用字典存储配置环境列表
config = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
