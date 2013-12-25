#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule, Version


class Module(BaseModule):
  name = 'amcharts'
  homepage = 'http://www.amcharts.com/'

  def _new_versions(self, cur_ver):
    if cur_ver is None or cur_ver == '0':
      start = 2
    else:
      start = int(cur_ver) + 1
    versions = []
    while True:
      if self.http_get('http://docs.amcharts.com/%s/' % start, suppress_error=True):
        versions.append(Version(start))
        start += 1
      else:
        break
    return versions

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.clear_source()
    options = {'cut-dirs': 2, 'domains': 'docs.amcharts.com'}
    ret = self.wget_mirror('http://docs.amcharts.com/%s/javascriptcharts/' % version, \
               self.source_dir, **options)
    if ret[0] in (0, 8):
      return self.source_dir
