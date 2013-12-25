#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'understanding-json-schema'
  homepage = 'http://spacetelescope.github.io/understanding-json-schema/'
  url = 'https://github.com/spacetelescope/understanding-json-schema'
  versioning = 'single'
  version = '4'

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.shell('make html')
    return os.path.join(os.getcwd(), 'build/html')
