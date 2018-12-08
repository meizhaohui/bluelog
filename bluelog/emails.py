#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/12/1 10:37
@File    : emails.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 邮件通知设置
"""
from threading import Thread
from flask import url_for, current_app
from flask_mail import Message

from bluelog.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_async_mail(subject, to, html):
    """异步发送邮件"""
    app = current_app._get_current_object()  # 获取被代理的真实对象
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id,
                       _external=True) + '#comments'
    send_async_mail(
        subject='New Comment',
        to=current_app.config['BLUELOG_ADMIN_EMAIL'],
        html=f'<p>New comment in post <i>{post.title}</i>,'
             f' click the link below to check:</p>'
             f'<p><a href="{post_url}">{post_url}</a></p>'
             f'<p><small style="color:#868e96">'
             f'Do not reply this email.</small></p>'
    )


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id,
                       _external=True) + '#comments'
    send_async_mail(
        subject='New Reply',
        to=comment.email,
        html=f'<p>New reply for the comment you left in post <i>{comment.post.title}</i>,'
             f' click the link below to check:</p>'
             f'<p><a href="{post_url}">{post_url}</a></p>'
             f'<p><small style="color:#868e96">'
             f'Do not reply this email.</small></p>'
    )
