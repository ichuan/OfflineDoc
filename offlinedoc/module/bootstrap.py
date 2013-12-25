#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'bootstrap'
  homepage = 'http://getbootstrap.com/'
  url = 'https://github.com/twbs/bootstrap'

  def entry(self, version):
    if version < Version('2.0.0'):
      return 'docs/index.html'
    return 'index.html'

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    if version < Version('2.0.0'):
      return os.getcwd()
    elif version < Version('3.0.0'):
      self.shell("sed -i '/platform.twitter.com/d' docs/*.html")
      return os.path.join(os.getcwd(), 'docs')
    else:
      self.shell('jekyll build')
      self.shell("sed -i '/platform.twitter.com/d' _gh_pages/index.html")
      self.shell("sed -i '/platform.twitter.com/d' _gh_pages/*/*.html")
      return os.path.join(os.getcwd(), '_gh_pages')
