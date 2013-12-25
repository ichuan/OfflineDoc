#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule, Version


# http://query.yahooapis.com/v1/public/yql?q=select * from html where url="http://api.mongodb.org/python/" and xpath='/html/body/ul/li/a'&format=json&callback=
YQL_URL = "http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url%3D%22http%3A%2F%2Fapi.mongodb.org%2Fpython%2F%22%20and%0A%20%20%20%20%20%20xpath%3D'%2Fhtml%2Fbody%2Ful%2Fli%2Fa'&format=json&callback="

class Module(BaseModule):
  '''
  pymongo's git repo(https://github.com/mongodb/mongo-python-driver) has a sphinx
  building script, but it sucks, I've never successfully calling it. That's why
  I have to wget mirror it.
  '''
  name = 'pymongo'
  homepage = 'http://www.mongodb.org/'

  def _new_versions(self, cur_ver):
    ret = self.yql_get(YQL_URL)
    versions = [Version(i['content']) for i in ret['a']]
    return sorted(i for i in versions if i > cur_ver)

  def post_update(self, version, ret=None):
    self.clear_source()
    options = {'cut-dirs': 2, 'domains': 'api.mongodb.org'}
    ret = self.wget_mirror('http://api.mongodb.org/python/%s/' % version, \
                            self.source_dir, **options)
    if ret[0] in (0, 8):
      return self.source_dir
