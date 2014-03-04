#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'mongoengine'
  homepage = 'http://mongoengine.org/'
  url = 'https://github.com/MongoEngine/mongoengine'
  version_by = 'tags'

  def _new_versions(self, cur_ver):
    vers = super(Module, self)._new_versions(cur_ver)
    # strip malformed tag like: v.0.6.11
    if vers:
      return [i for i in vers if not i.startswith('.')]

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    # install deps
    if os.path.isfile('requirements.txt'):
      self.logger.info('Installing pip requirements ...')
      self.shell('pip install -r requirements.txt')
    self.pushd('docs')
    self.logger.info('Running sphinx-building ...')
    self.shell('make clean html')
    self.shell(r'find _build/html/ -name "*.html" -exec '
                'sed -i "/\/\/fonts.googleapis.com/d" '
                '{} \;')
    self.popd()
    return os.path.join(os.getcwd(), 'docs/_build/html/')
