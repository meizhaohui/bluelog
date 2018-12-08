#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/18 20:13
@File    : auth.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 认证蓝图
"""

from flask import redirect, url_for, Blueprint, flash, render_template
from flask_login import current_user, login_user, logout_user, login_required

from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    """登陆视图"""
    if current_user.is_authenticated:
        # 如果用户认证通过，则跳转到博客首页
        return redirect(url_for('blog.index'))

    # 没有认证通过的话，则需要用户登陆
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if admin.validate_password(password):
                login_user(admin, remember)  # 登陆用户
                flash('Welcome back.', 'info')
                return redirect_back()  # 返回上一个页面
            flash('Invalid password.', 'warning')
        else:
            flash('Invalid username.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout/')
@login_required
def logout():
    """注销视图"""
    logout_user()  # 注销用户
    flash('Logout success.', 'info')
    return redirect_back()  # 返回上一个页面
