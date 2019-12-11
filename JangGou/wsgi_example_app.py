#!/usr/bin/python
# -*- coding:utf-8 -*-
# author:joel 18-6-5


def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'hello world']