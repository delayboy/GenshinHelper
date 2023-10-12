#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @time: 2021/5/26 14:17
# @File: create_pyd_file.py
import os
import shutil
import time
import sys


def func(path):
    folder_path = os.path.dirname(path)

    file_path = os.path.split(path)[1]
    os.chdir(folder_path)
    with open('setup.py', 'w') as f:
        f.write('from setuptools import setup\n')
        f.write('from Cython.Build import cythonize\n')
        f.write('setup(\n')
        f.write("name='test',\n")
        f.write("ext_modules=cythonize('%s',language_level='3')\n" % file_path)
        f.write(")\n")
    os.system('python setup.py build_ext --inplace')  # python setup.py build_ext --inplace
    filename = file_path.split('.py')[0]
    time.sleep(2)
    # 这里的cp37-win_amd64需要注意一下，这个是依据python解释器类型以及windows版本生成的，建议是单个生成一个pyd文件然后相应修改一下
    new_path = '%s\\%s.pyd' % (folder_path, filename)
    if os.path.exists(new_path):
        os.remove(new_path)
    os.rename('%s\\%s.cp311-win_amd64.pyd' % (folder_path, filename), '%s\\%s.pyd' % (folder_path, filename))
    # 这个是删除py源文件，测试的时候可以先注释掉查看效果
    os.remove('%s.c' % filename)
    build_folder_path = os.path.join(folder_path, 'build')
    # 删除掉生成的build文件夹
    shutil.rmtree(build_folder_path)
    os.remove('setup.py')
    os.remove(file_path)


def delete_all_in_dir(dir_path: str):
    if not os.path.exists(dir_path):
        return

    print(f"存在{dir_path}文件夹，进行清理")
    # 设置topdown参数进行深度优先遍历
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)
        for dir_name in dirs:
            sub_dir_path = os.path.join(root, dir_name)
            if os.path.exists(sub_dir_path):
                os.removedirs(sub_dir_path)

    if os.path.exists(dir_path):
        os.removedirs(dir_path)


def get_all_file(path):
    build_dir = os.path.join(path, "build")
    delete_all_in_dir(build_dir)

    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            if name.endswith(".py") and (not name.__eq__("setup.py")) and (not name.__eq__("pyd_main.py")):
                func(file_path)
            elif name.endswith(".spec") or name.endswith(".txt") or name.endswith(".log"):
                os.remove(file_path)


paths = os.path.abspath("py_files")  # sys.argv[1]
get_all_file(paths)
