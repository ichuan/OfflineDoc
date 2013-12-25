#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

'''
既非标准 github/svn 项目，又不是单一HTML文档的项目，只要它有在线文档可以看
就可以用这一终极的 wget 镜像大法抓下来
'''

import os
import re
from offlinedoc.module._base import BaseModule, Version


# 使用 YQL 解析 HTML，提取版本号
# http://query.yahooapis.com/v1/public/yql?q=select * from html where url="http://api.jquery.com/" and xpath='//div[@id="sidebar"]//a/text()[starts-with(.,"Version ")]'&format=json&callback=
YQL_URL = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fapi.jquery.com%2F%22%20and%0A%20%20%20%20%20%20xpath%3D'%2F%2Fdiv%5B%40id%3D%22sidebar%22%5D%2F%2Fa%2Ftext()%5Bstarts-with(.%2C%22Version%20%22)%5D'&format=json&callback="

class Module(BaseModule):
  '''
  '''
  # 唯一 id（格式要求同 Linux 文件名）
  name = 'jquery'
  # 主页，获取 favicon 用（没有的话可以为 None）
  homepage = 'http://jquery.com/'
  # 版本类型
  #   normal: 递增，保留所有版本（例如：bootstrap）
  #   latest: 递增，只保留最新版本（例如：jquery）
  #   single: 只抓取一次，无论新旧（例如：sed）
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    versions = [
      Version(i)
      for i in re.findall(r'Version ([\d\.]+)', self.yql_get(YQL_URL))
    ]
    return [i for i in versions if i > cur_ver]

  def post_update(self, version, ret=None):
    '''
    需要返回一个包含生成的 HTML 文档的目录地址
    当前已经在 git clone 出来的代码目录中了
    '''
    # 先清空自己的源码目录
    self.clear_source()
    # 然后 wget 镜像，放到源码目录，限制只抓取 api.jquery.com 下链接
    ret = self.wget_mirror('http://api.jquery.com/', self.source_dir, \
                            domains='api.jquery.com')
    # 如果 wget 成功，先替换掉 html 中的外链（会减慢浏览速度），然后返回源码目录（含生成的 HTML 文档）
    if ret[0] == 0:
      self.shell(r'find %s -name "*.html" -exec '
                  'sed -i "/\/\/use.typekit.net/d" '
                  '{} \;' % self.source_dir)
      return self.source_dir

