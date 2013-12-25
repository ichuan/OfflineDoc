#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'django'
  homepage = 'https://www.djangoproject.com/'
  url = 'https://github.com/django/django'
  version_by = 'tags'

  def post_update(self, version, ret=None):
    self.pushd('docs')
    if version < Version('1.2.1'):
      # docs bug: https://groups.google.com/forum/#!topic/django-users/10i5SrQ3ctY
      self.logger.info('Fixing djangodocs.py ...')
      open('_ext/djangodocs.py', 'w+').write(self.http_get(
        'https://github.com/django/django/raw/stable/1.2.x/docs/_ext/djangodocs.py'
      ))
    self.logger.info('Running sphinx-build ...')
    self.shell('make html')
    self.popd()
    return os.path.join(os.getcwd(), 'docs/_build/html/')
