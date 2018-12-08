#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/11/17 9:01
@File    : commands.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 自定义Flask命令
"""

import click

from bluelog.extensions import db


def register_commands(app):
    @app.cli.command()
    def initdb():
        # 新建数据表
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--category', default=10,
                  help='Quantity of categories, default is 10.')
    @click.option('--post', default=50,
                  help='Quantity of posts,default is 50.')
    @click.option('--comment', default=500,
                  help='Quantity of comments,default is 500.')
    @click.option('--tag', default=10,
                  help='Quantity of tags,default is 10.')
    def forge(category, post, comment, tag):
        """Generate fake data"""
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, \
            fake_comments
        db.drop_all()
        db.create_all()

        click.echo('Working...')
        click.echo('Generating the administrator...')
        fake_admin()

        click.echo(f'Generating {category} categories...')
        fake_categories(category)

        click.echo(f'Generating {post} posts...')
        fake_posts(post)

        click.echo(f'Generating {comment} comments...')
        fake_comments(comment)

        click.echo(f'Done!!!')
