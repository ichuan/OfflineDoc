#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule


class Module(BaseModule):
    '''
    '''
    name = 'bash'
    version = '3.9.1'
    versioning = 'single'
    url = 'https://github.com/mofaph/abs-guide-cn/tarball/master'

    def post_update(self, version, ret):
      self.clear_source()
      self.pushd(self.source_dir)
      ret = self.shell('wget %s -O file' % self.url)
      if ret[0] == 0:
        if self.shell('tar xf file')[0] == 0:
          self.shell('rm file')
          p = os.listdir('.')[0]
          self.popd()
          return os.path.join(self.source_dir, p, 'html')
