#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/18 20:14
@File    : admin.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 管理员蓝图
"""
import datetime
import logging
import os

from flask import render_template, Blueprint, flash, redirect, url_for
from flask import request, current_app
from flask_ckeditor import upload_success, upload_fail
from flask_login import current_user, login_required

from bluelog.extensions import db
from bluelog.forms import SettingsForm, PostForm, CategoryForm
from bluelog.models import Post, Category, Comment
from bluelog.utils import redirect_back, random_filename

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger('flask.app')


@admin_bp.before_request
@login_required
def login_protect():
    pass


@admin_bp.route('/post/manage/')
def manage_post():
    """文章管理"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_POST_PER_PAGE']
    # 按时间升序排列，获取评论的分页对象
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page)
    posts = pagination.items
    return render_template('admin/manage_post.html',
                           pagination=pagination,
                           posts=posts)


@admin_bp.route('/post/new/', methods=['GET', 'POST'])
def new_post():
    """创建文章"""
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(
            title=title,
            body=body,
            category=category)
        db.session.add(post)
        db.session.commit()
        flash('Post Created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit/', methods=['GET', 'POST'])
def edit_post(post_id):
    """编辑文章"""
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        post.timestamp = datetime.datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        flash('Post Updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete/', methods=['POST'])
def delete_post(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@admin_bp.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    """新建分类"""
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        print('category_name', name)
        category = Category.query.filter_by(name=name).first()
        if category:
            logger.info('category:%s exist', category.name)
            flash('Category exist,please change the name', 'warning')
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added.', 'success')
        return redirect_back()
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/manage/')
def manage_category():
    """管理分类"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_CATEGORY_PER_PAGE']
    pagination = Category.query.order_by(Category.id.asc()).paginate(page,
                                                                     per_page=per_page)
    categories = pagination.items
    return render_template('admin/manage_category.html',
                           categories=categories,
                           pagination=pagination)


@admin_bp.route('/category/<int:category_id>/delete/', methods=['POST'])
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    if category.name == 'default':
        flash("You can't delete the default category.", 'warning')
        return redirect(url_for('admin.manage_category'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.manage_category'))


@admin_bp.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def edit_category(category_id):
    """修改分类"""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        if form.name.data == Category.query.get(1).name:
            flash(
                "You can't move the category name to the default category name.",
                'warning')
            return redirect(url_for('admin.manage_category'))
        category.name = form.name.data
        db.session.commit()
        flash('Category edited.', 'success')
        return redirect(url_for('admin.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/comment/manage/')
def manage_comment():
    """管理评论"""
    filter_rule = request.args.get('filter', 'all')  # 设置查询规则
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filter_comments = Comment.query.filter(Comment.reviewed == False)
    elif filter_rule == 'admin':
        filter_comments = Comment.query.filter_by(from_admin=True)
    else:
        filter_comments = Comment.query
    pagination = filter_comments.order_by(
        Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html',
                           comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/delete/', methods=['POST'])
def delete_comment(comment_id):
    """删除评论"""
    next_url = request.args.get('next')
    logger.info('next_url:%s', next_url)

    if next_url.startswith('/post'):
        # 在文章中删除评论
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted.', 'success')
        return redirect_back()
    else:
        # 在评论管理中删除评论

        # 获取每页显示的评论数
        per_page = current_app.config['BLUELOG_MANAGE_COMMENT_PER_PAGE']
        # 计算当前剩余的总评论数
        filter_rule = request.args.get('filter')
        current_page = int(request.args.get('current_page'))
        if filter_rule == 'unread':
            comments_numbers = Comment.query.filter(
                Comment.reviewed == False).count()
        elif filter_rule == 'admin':
            comments_numbers = Comment.query.filter_by(from_admin=True).count()
        else:
            comments_numbers = Comment.query.count()
        logger.info('filter_rule:%s', filter_rule)
        logger.info('comments_numbers:%s', comments_numbers)
        logger.info('current_page:%s', current_page)
        # 删除评论
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted.', 'success')

        # 判断是否是最后一页，解决删除最后一页时找不到原来页的问题
        if int((comments_numbers - 1) / per_page) == (current_page - 1) \
                and (comments_numbers - 1) % per_page == 0:
            new_page = current_page - 1
            logger.info('new_page:%s', new_page)
            return redirect(url_for('admin.manage_comment',
                                    filter=filter_rule,
                                    page=new_page))
        else:
            return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/approve/', methods=['POST'])
def approve_comment(comment_id):
    """评审评论"""
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment Approved.', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/setcomment/', methods=['POST'])
def set_comment(post_id):
    """设置文章是否开启评论功能"""
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'info')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'info')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/settings/', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        current_user.name = form.name.data,
        current_user.blog_title = form.blog_title.data,
        current_user.blog_sub_title = form.blog_sub_title.data,
        current_user.about = form.about.data
        db.session.commit()
        flash('Settings Updated.', 'info')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/upload/', methods=['POST'])
def upload():
    f = request.files.get('upload')
    suffix = os.path.splitext(f.filename)[-1].lower()
    # 如果后缀不满足要求
    if suffix not in {'.png', '.jpg', '.jpeg', '.bmp'}:
        return upload_fail('Please upload image that suffix is .png|.jpg|.jpeg|.bmp')
    # 新文件的名称
    new_filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], new_filename))
    url = url_for('blog.uploaded_files', filename=new_filename)
    return upload_success(url)
