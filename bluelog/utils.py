#!/usr/bin/python3
"""
@Author  : Zhaohui Mei(梅朝辉)
@Email   : mzh.whut@gmail.com

@Time    : 2018/12/1 10:11
@File    : utils.py
@Version : 1.0
@Interpreter: Python3.6.2
@Software: PyCharm

@Description: 工具函数集合
"""
import os
from uuid import uuid4

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in (
    'http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def random_filename(filename):
    """生成全球唯一码的文件名
    output example: 5228331683fc43208ed58ecac706012e.png
    """
    suffix = os.path.splitext(filename)[-1].lower()
    filename = uuid4().hex + suffix
    return filename
