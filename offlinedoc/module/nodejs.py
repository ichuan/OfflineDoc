#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule, Version


class Module(BaseModule):
  '''
  '''
  name = 'nodejs'
  homepage = 'http://nodejs.org/'

  def _new_versions(self, cur_ver):
    ret = self.http_get('http://nodejs.org/docs/')
    versions = map(Version, re.findall(r'<a href="v([\.0-9]+)/">', ret))
    return sorted(i for i in versions if i > cur_ver)

  def post_update(self, version, ret=None):
    self.clear_source()
    options = {'cut-dirs': 2, 'domains': 'nodejs.org'}
    ret = self.wget_mirror('http://nodejs.org/docs/v%s/' % version, \
                            self.source_dir, **options)
    # http://www.gnu.org/software/wget/manual/html_node/Exit-Status.html
    # http://nodejs.org/docs/v0.6.7/ returns 8, but everything is ok
    if ret[0] in (0, 8):
      return self.source_dir
