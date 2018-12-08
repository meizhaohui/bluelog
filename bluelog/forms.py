#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/16 20:52
@File    : forms.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 表单
"""

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, \
    PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, URL

from bluelog.models import Category


# 注：validators=[DataRequired()] DataRequired这个验证器一定要加括号()
# 否则会报错误
# TypeError: __init__() takes from 1 to 2 positional arguments but 3 were given


class CommentForm(FlaskForm):
    """普通用户发表评论的表单"""
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site',
                       validators=[Optional(), URL(), Length(0, 254)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AdminCommentForm(CommentForm):
    """管理员发表评论的表单"""
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LoginForm(FlaskForm):
    """登陆表单"""
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me', validators=[])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    """文章表单"""
    title = StringField('Title',
                        validators=[DataRequired(), Length(1, 60)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.name).all()
                                 ]


class CategoryForm(FlaskForm):
    """文章分类表单"""
    name = StringField('Title',
                       validators=[DataRequired(), Length(1, 30)],
                       render_kw={'placeholder': 'input the category here'},
                       description='Category length 1-30')
    submit = SubmitField('Submit')


class SettingsForm(FlaskForm):
    """设置表单"""
    name = StringField('Name',
                       validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title',
                             validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title',
                                 validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    """搜索文章表单，使用render_kw指定表单字段的样式"""
    key_word = StringField('', validators=[DataRequired()],
                           render_kw={'class': 'form-control',
                                      'style': 'width:300px;',
                                      'placeholder': 'Search keyword in Post Title or Post Body'},
                           description='input the keyword')
    submit = SubmitField('Search', render_kw={'class': 'btn btn-success'})
