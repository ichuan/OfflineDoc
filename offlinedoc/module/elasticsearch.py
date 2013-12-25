#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

'''
项目放在 github 上的项目
'''

import os
import re, yaml
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  # 唯一 id（格式要求同 Linux 文件名）
  name = 'elasticsearch'
  # 主页，获取 favicon 用（没有的话可以为 None）
  homepage = 'http://www.elasticsearch.org/'
  # 项目地址（可以 git clone 的地址）
  url = 'https://github.com/elasticsearch/docs'
  # 版本类型
  #   normal: 递增，保留所有版本（例如：bootstrap）
  #   latest: 递增，只保留最新版本（例如：jquery）
  #   single: 只抓取一次，无论新旧（例如：sed）
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    txt = self.http_get(
      'https://github.com/elasticsearch/docs/raw/master/conf.yaml'
    )
    try:
      obj = yaml.safe_load(txt)
      ver = Version(obj['repos']['elasticsearch']['current'])
      if ver > cur_ver:
        return ver
    except Exception, e:
      self.logger.warn('Parse version error: %s' % e)
    return []

  def post_update(self, version, ret=None):
    '''
    需要返回一个包含生成的 HTML 文档的目录地址
    当前已经在 git clone 出来的代码目录中了
    '''
    return os.path.join(os.getcwd(), 'html')
