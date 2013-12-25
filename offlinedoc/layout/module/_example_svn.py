#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

'''
项目源码放在 svn 上的项目
'''

import os
import re
from offlinedoc.module._base import SvnModule, Version


class Module(SvnModule):
  '''
  '''
  # 唯一 id（格式要求同 Linux 文件名）
  name = 'project'
  # 主页，获取 favicon 用（没有的话可以为 None）
  homepage = None
  # 项目地址（可以 svn checkout 的地址）
  url = 'https://svn.example.com/project/trunk/'
  # 版本类型
  #   normal: 递增，保留所有版本（例如：bootstrap）
  #   latest: 递增，只保留最新版本（例如：jquery）
  #   single: 只抓取一次，无论新旧（例如：sed）
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    '''
    检查新版本，需要更新时返回较新的版本的列表（或单个版本号）
    无须更新时返回 False 或 None
    '''
    ret = self.shell(
      '''svn cat %s/sphinx/conf.py | grep -oP "(?<=release = ')[^']+"'''
      % self.url
    )
    # self.shell 函数返回一个 tuple，第一个元素是进程退出值（0 表示正常结束），另一个元素是标准输出内容
    if ret[0] == 0:
      ver = Version(ret[1].strip())
      if ver > cur_ver:
        return ver

  def post_update(self, version, ret=None):
    '''
    需要返回一个包含生成的 HTML 文档的目录地址
    当前已经在 git clone 出来的代码目录中了
    '''
    # cd 到 docs/sphinx 目录
    self.pushd('docs/sphinx')
    # 执行 make clean html，后台会进行 shpinx 编译
    self.shell('make clean html')
    # 返回代码目录
    self.popd()
    # 返回包含 HTML 文档的目录地址
    return os.path.join(os.getcwd(), 'docs/sphinx/_build/html')

