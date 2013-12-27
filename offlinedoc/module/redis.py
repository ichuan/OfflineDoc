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


class Module(BaseModule):
  '''
  '''
  # 唯一 id（格式要求同 Linux 文件名）
  name = 'redis'
  # 主页，获取 favicon 用（没有的话可以为 None）
  homepage = 'http://redis.io/'
  # 版本类型
  #   normal: 递增，保留所有版本（例如：bootstrap）
  #   latest: 递增，只保留最新版本（例如：jquery）
  #   single: 只抓取一次，无论新旧（例如：sed）
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    versions = [
      Version(i)
      for i in re.findall(r'http://download.redis.io/releases/redis-([\.\d]+).tar.gz', self.http_get(self.homepage))
    ]
    return [i for i in versions if i > cur_ver]

  def post_update(self, version, ret=None):
    '''
    需要返回一个包含生成的 HTML 文档的目录地址
    '''
    # 先清空自己的源码目录
    self.clear_source()
    # 然后 wget 镜像，放到源码目录，限制只抓取 api.jquery.com 下链接
    ret = self.wget_mirror('http://redis.io/', self.source_dir, \
                            domains='redis.io')
    # 如果 wget 成功，先替换掉 html 中的外链（会减慢浏览速度），然后返回源码目录（含生成的 HTML 文档）
    if ret[0] in (0, 8):
      self.shell(r'find %s -name "*.html" -exec '
                  'sed -i "/disqus.com\/embed.js/d" '
                  '{} \;' % self.source_dir)
      return self.source_dir
