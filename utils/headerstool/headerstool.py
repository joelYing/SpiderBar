#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2018/8/14 15:36


def headerstool():
    """deal with the request headers"""
    with open('format_headers.txt', 'w') as fw:
        with open('headers.txt', 'r') as fr:
            for line in fr.readlines():
                if not line.endswith('\n'):
                    line = line + '\n'
                line_w = '\'' + line.replace(': ', '\': \'').replace('\n', '\',\n')
                fw.writelines(line_w)


if __name__ == '__main__':
    headerstool()

