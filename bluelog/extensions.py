#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/18 20:53
@File    : extensions.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description:  扩展类实例化
"""
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# 创建对象
bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
mail = Mail()
login_manager = LoginManager()  # 用户登陆管理
csrf = CSRFProtect()  # 使用CSRFProtect实现CSRF保护

# 视图保护设置
login_manager.login_view = 'auth.login'  # 未登陆时跳转到这个视图来
login_manager.login_message_category = 'warning'  # 消息类型
#　未登陆访问保护视图时的消息提示
login_manager.login_message = 'Please login to access this page.(请先登陆！)'


@login_manager.user_loader
def load_user(user_id):
    """用户加载函数，FLask-Login用于获取当前用户的对象，必须要设置"""
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user
