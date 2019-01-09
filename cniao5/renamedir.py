#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:joel
# time:2019/1/3 13:37

import os
import random
import re
import requests

basic_path = 'D:\\pyprogram\\Work\\cniao5\\{}'


def mkd():
    """模拟递归创建文件夹及文件夹下随机数目的文件"""
    x = 1
    for num in range(1, 25):
        path = basic_path.format(num)
        if os.path.exists(path):
            print('ok')
        else:
            os.makedirs(path)
            for i in range(1, random.randint(2, 17)):
                txt_path = path + '\\lesson{}.txt'.format(x)
                with open(txt_path, 'w') as f:
                    f.write('cniao5')
                x += 1


def dirnum():
    """路径下文件总数"""
    path = 'D:\\pyprogram\\Work\\cniao5'
    count = 0
    for root, dirs, files in os.walk(path):
        for each in files:
            print(each)
            count += 1
    print(count)


def renamefile():
    """文件重命名"""
    path = 'D:\\Python\\PycharmProject\\FinalCniao5'

    names = ['Andfix简介、接入演示、源码分析', '实现自定义自己的Andfix01', '实现自定义自己的Andfix02',
             '实现自定义自己的Andfix03', 'JNI与NDK概要', 'JNI数据类型与指针嵌套', 'JNI属性', 'JNI方法数组引用',
             'JNI异常处理', 'JNI缓存策略', '常用工具', '冒泡排序', '选择排序', '插入排序', '三种排序效率对比',
             'MVC讲解_小案例', 'MVP讲解_小案例', 'DataBinding讲解', 'MVVM讲解-小案例', '项目讲解MVC',
             '项目实现MVP', '项目实现MVVM讲解1', '项目实现MVVM讲解2-总结', '快速使用', 'Http协议介绍',
             'Get请求（获取用户信息为例）', 'Post请求（Form表单形式）', 'Post请求（JSON参数形式）',
             '文件下载（简单方式）', '文件下载（拦截器方式）', 'OkHttp简单封装1', 'OkHttp简单封装2',
             '为什么要使用Dagger2', 'Dagger2的基本使用', '模块化实现', '创建和区分不同实例', 'Singleton 单例讲解',
             '自定义Scope', 'SubCompnet和Lazy与Provider', '基本介绍', '快速上手体验', 'GET请求介绍',
             'Post请求介绍', '与RxJava结合使用', '断点续传01', '断点续传02', '断点续传03', '功能分析',
             '添加HeaderView', '事件监听', '开课-从源码的角度分析UI绘制流程-上', '开课-从源码的角度分析UI绘制流程-下',
             '开篇_介绍', '反射_讲解', '注解_讲解', '完成ButterKnife框架', '课程简介', '自定义圆形的ImageView',
             '自定义Dialog', '调用系统功能及总结', 'App效果演示and技术介绍', 'DrawerLayout_NavigationView实现侧滑菜单',
             'DrawerLayout_Toolbar 整合', 'TabLayout_ViewPager_Fragment可滑动的顶部菜单', '在Android上使用SVG矢量图',
             '在Android中使用iconfont图标', '自定义iconfont ', 'RecycleView 的简单实用', ' MVP 架构讲解',
             ' MVP 架构实战', '课程大纲', '了解直播及腾讯云直播', '基础封装', '网络封装', '接口协议', 'MVP架构讲解',
             ' 注册功能', '登录功能', ' 腾讯IM登录', '底部导航', '项目讲解', '项目知识点讲解', '欢迎页—申请权限',
             '沉浸式状态栏实现', 'BaseAcitivity', 'HomeActivity_TabLayout', '界面显示逻辑', 'BaseFragment抽取',
             'LoadingPager的抽取', 'MVP讲解', 'APP的展示介绍', '项目分包', '别开生面的启动页', '视频引导页',
             '视频引导页的问题解决', 'gradle的基本配置', '主界面的基本布局实现（新版）', '主布局界面完成(新版)',
             'mvp的基本介绍', 'mvp的基本实现', '课程大纲及运行效果介绍', '用fragmentTabHost 实现底部菜单',
             'ToolBar的基本使用', '自定义ToolBar', '酷炫轮播广告', 'RecyclerView 详细介绍', '首页商品分类',
             'okHttp的使用', 'OkHttp简单封装', '主页商品分类重构', 'App效果演示', '提高10倍开发效率-Android Studio配置',
             '欢迎界面的实现', '引导界面的实现', '使用.FragmentTabhost构建底部Tab菜单', '广告条的基本实现',
             '自定义控件的基本讲解', '自定义广告条indicator控件-基础篇', '自定义广告条indicator控件-封装篇',
             'toolbar的基本使用(上)', 'BaseActivity 与 BaseFragment 的封装(上)',
             'BaseActivity 与 BaseFragment 的封装(下)', 'ToolBar 的使用介绍', 'ToolBar 的封装',
             'FragmentTabHost 实现底部 Tab', '启动页与授权登录', '获取最新微博信息', '新浪微博网络通信层封装',
             'RecyclerView 的使用介绍', 'Glide 使用介绍', '重36Kr网站改版调整【重要（补）】', '菜鸟新闻-功能介绍',
             '拖拽控件（ViewDragHelper）讲解', '启动界面和主框架实现讲解', '沉浸式状态栏讲解', 'Jsoup数据爬虫介绍',
             '抓取广告分类与文章分类数据', '抓取文章详情标签作者信息', '左侧功能菜单实现', '网易新闻滑动菜单效果实现',
             '课程介绍', '准备工作', '文件目录', 'app.json 配置文件介绍', '编辑器的选择', '模块化', '页面注册page函数',
             '视图层（上）', '课程项目演示', '开发流程介绍', 'Sublime3 工具安装', 'onload 事件介绍',
             'canvas基础', 'sonic基础介绍', 'loding代码实现', 'fullpage的基础介绍', 'spring boot 简介',
             'spring boot-HelloWorld', 'spring boot-两种启动方式', '修改启动图标及端口号', '全局异常处理',
             'springboot 集成jsp', '(操作数据库)spring boot 集成mybatis', '(模板数据填充)springboot集成freeMarker',
             'spring boot 静态资源访问', 'spring boot 集成log4j', 'spring boot 多数据源配置', 'spring boot 拦截器',
             'spring boot 定时器', 'spring boot 自定义参数配置', 'spring boot 缓存', 'springboot 打包发布',
             'spring boot 多环境配置', 'spring boot 跨域', 'spring boot 验证', 'spring boot 单元测试',
             'vmware虚拟机的安装', 'centos6.9操作系统的安装', 'linux基本命令使用', '作业1', '作业1讲解',
             'python介绍', 'python安装', 'python虚拟环境的安装', '第一个python程序', 'pycharm（Python开发神器）的使用',
             '作业2', '作业2讲解', '变量、整型、浮点型、字符串类型', '空值、布尔值、列表、元组、字典、集合',
             'if条件语句、input函数', '循环语句', '作业3', '作业3讲解', '函数介绍、函数的定义、函数的调用、函数的参数',
             '函数的返回值', '全局变量和局部变量', '作业4', '作业4讲解', '学生管理系统框架',
             '学生管理系统的增加和查看模块的编写', '学生管理系统的修改和删除、家庭作业']
    for i in range(1, 25):
        dirs = path + '\\{}'.format(i)
        print(dirs)
        for j in os.listdir(dirs):
            """ 
            一开始将 lessons1.mp4 - > Andfix简介、接入演示、源码分析.mp4
            后来觉得还得加上序号 Andfix简介、接入演示、源码分析.mp4 - > 1、Andfix简介、接入演示、源码分析.mp4
            """
            # n = re.findall(r'lessons(\d+).mp4', j)[0]
            # os.rename(dirs + '\\' + j, dirs + '\\' + str(names[int(n) - 1]) + '.mp4')

            n = names.index(re.findall(r'(.*?).mp4', j)[0])
            os.rename(dirs + '\\' + j, dirs + '\\' + str(n + 1) + '、' + j)


def gethtml():
    """获取所有课程的名称"""
    names = []
    r = requests.get('https://www.cniao5.com/api/v1/course/10153/chapters')
    r_json = r.json()
    for l in r_json:
        for lesson in l['lessons']:
            names.append(lesson['name'])
    print(names)


if __name__ == '__main__':
    renamefile()
    # mkd()
    # gethtml()
