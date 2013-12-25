#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule, Version


# http://query.yahooapis.com/v1/public/yql?q=select * from html where url="http://api.jquery.com/" and xpath='//div[@id="sidebar"]//a/text()[starts-with(.,"Version ")]'&format=json&callback=
YQL_URL = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fapi.jquery.com%2F%22%20and%0A%20%20%20%20%20%20xpath%3D'%2F%2Fdiv%5B%40id%3D%22sidebar%22%5D%2F%2Fa%2Ftext()%5Bstarts-with(.%2C%22Version%20%22)%5D'&format=json&callback="

class Module(BaseModule):
  '''
  '''
  name = 'jquery'
  homepage = 'http://jquery.com/'
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    versions = [
      Version(i)
      for i in re.findall(r'Version ([\d\.]+)', self.yql_get(YQL_URL))
    ]
    return [i for i in versions if i > cur_ver]

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.clear_source()
    ret = self.wget_mirror('http://api.jquery.com/', self.source_dir, \
                            domains='api.jquery.com')
    if ret[0] in (0, 8):
      self.shell(r'find %s -name "*.html" -exec '
                  'sed -i "/\/\/use.typekit.net/d" '
                  '{} \;' % self.source_dir)
      return self.source_dir

