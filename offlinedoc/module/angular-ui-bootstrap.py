#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'angular-ui-bootstrap'
  homepage = 'http://angular-ui.github.io/bootstrap/'
  url = 'https://github.com/angular-ui/bootstrap'
  version_by = 'tags'

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.logger.info('Running npm install ...')
    self.shell('npm cache clean; npm install')
    self.logger.info('Running grunt build ...')
    if version < Version('0.3.0'):
      self.shell('grunt -- build html2js site')
    else:
      self.shell('grunt --force')
    return os.path.join(os.getcwd(), 'dist')
