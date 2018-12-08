#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/18 20:11
@File    : blog.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description:  博客蓝图
"""
import logging

from flask import render_template, flash, redirect, url_for, request, \
    current_app, Blueprint, abort, make_response, send_from_directory
from flask_login import current_user
from sqlalchemy import or_

from bluelog.emails import send_new_comment_email, send_new_reply_email
from bluelog.extensions import db
from bluelog.forms import CommentForm, AdminCommentForm, SearchForm
from bluelog.models import Post, Category, Comment
from bluelog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)
logger = logging.getLogger('flask.app')


# 不添加搜索功能的index视图函数
# @blog_bp.route('/')
# def index():
#     logger.info('index')
#     # 获取当前页数
#     page = request.args.get('page', 1, type=int)
#     # 每页显示的文章数
#     per_page = current_app.config['BLUELOG_POST_PER_PAGE']
#     # 分页对象，降序排序
#     pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
#                                                                      per_page=per_page)
#     # 当前页的记录列表
#     posts = pagination.items
#     return render_template('blog/index.html', pagination=pagination,
#                            posts=posts)


@blog_bp.route('/', methods=['GET', 'POST'])
def index():
    logger.info('index')
    # 获取当前页数
    page = request.args.get('page', 1, type=int)
    # 每页显示的文章数
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    # 增加搜索文章功能
    search_form = SearchForm()
    if search_form.validate_on_submit():
        key_word = search_form.key_word.data
        return redirect(url_for('blog.index', key_word=key_word))
    key_word = request.args.get('key_word')
    if key_word:
        pagination = Post.query.filter(or_(
            Post.title.contains(key_word),
            Post.body.contains(key_word))).order_by(
            Post.timestamp.desc()).paginate(page, per_page=per_page)
    else:
        # 分页对象，降序排序
        pagination = Post.query.order_by(
            Post.timestamp.desc()).paginate(page, per_page=per_page)
    # 当前页的记录列表
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination,
                           posts=posts, search_form=search_form)


@blog_bp.route('/about/')
def about():
    logger.info('about')
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>/')
def show_category(category_id):
    """显示文章分类"""
    logger.info('show_category')
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category,
                           pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>/', methods=['GET', 'POST'])
def show_post(post_id):
    """文章显示"""
    logger.info('show_post')
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    logger.info('current_user.is_authenticated:%s',
                current_user.is_authenticated)
    # 按时间升序排列，获取评论的分页对象
    if current_user.is_authenticated:
        # 对于管理员，显示所有的评论，没有评审的也显示在界面上，方便后面approve
        # 所有的评论（包括review和未review的）
        pagination = Comment.query.with_parent(post).order_by(
            Comment.timestamp.asc()).paginate(page, per_page)
        comments = pagination.items
        # 所有的评论数（包括review和未review的）
        sum_comments = Comment.query.with_parent(post).all()
    else:
        # 只是评审通过（Approve）的评论才会显示在界面上
        pagination = Comment.query.with_parent(post).filter_by(
            reviewed=True).order_by(Comment.timestamp.asc()).paginate(
            page, per_page)
        comments = pagination.items
        sum_comments = Comment.query.with_parent(post).filter_by(
            reviewed=True).all()

    if current_user.is_authenticated:  # 如果当前用户已经登陆，使用管理员表单
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_ADMIN_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:  # 如果未登陆，则使用普通的评论表单
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():  # 使用POST请求，提交表单验证通过
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        # 实例化Comment评论对象
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)
        # 获取URL参数中reply对应的回复评论的ID
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            logger.info('send_new_reply_email')
            send_new_reply_email(replied_comment)  # 发送回复邮件
        # 将评论保存到数据库中
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.',
                  'info')
            # 发送新评论通知邮件
            logger.info('send_new_comment_email')
            send_new_comment_email(post)  # send notification email to admin
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination,
                           form=form, comments=comments,
                           sum_comments=sum_comments)


@blog_bp.route('/reply/comment/<int:comment_id>/')
def reply_comment(comment_id):
    """回复评论"""
    logger.info('reply_comment')
    comment = Comment.query.get_or_404(comment_id)
    # 获取当前页的page数，并传入到return语句中，解决点击Reply跳转到第1页的问题
    current_page = int(request.args.get('page', 1))
    # 如果文章关掉了评论功能，则点击“Reply”时会提示“Comment is disabled.”
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id,
                page=current_page, author=comment.author) + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>/')
def change_theme(theme_name):
    logger.info('change_theme')
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    # 设置cookie，保存30天   2592000秒 = 30 * 24 * 60 * 60
    response.set_cookie('theme', theme_name, max_age=2592000)
    return response


@blog_bp.route('/uploads/<filename>/')
def uploaded_files(filename):
    """获取图片文件"""
    path = current_app.config['UPLOADED_PATH']  # 上传文件存放的文件夹
    return send_from_directory(path, filename)
