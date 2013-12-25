#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import BaseModule, Version


class Module(BaseModule):
  '''
  '''
  name = 'python'
  homepage = 'http://python.org/'

  def _new_versions(self, cur_ver):
    ret = self.http_get('http://docs.python.org/ftp/python/doc/')
    versions = map(Version, re.findall(r'<a href="([0-9]\.[\.0-9a-zA-Z]+)/">', ret))
    return sorted(i for i in versions if i > cur_ver)

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.clear_source()
    self.pushd(self.source_dir)
    # 1.1
    if version == Version('1.1'):
      open('index.html', 'w+').write(
        self.http_get('http://docs.python.org/ftp/python/doc/1.1/quick-ref.1.1.html')
      )
      self.popd()
      return self.source_dir
    # pre 1.5
    elif version <= Version('1.5'):
      url = 'http://docs.python.org/ftp/python/doc/%s/html-%s.tar.gz' % (version, version)
    # 1.6
    elif version == Version('1.6'):
      url = 'http://docs.python.org/ftp/python/doc/1.6/html-1.6p1.tgz'
    # pre 2.4
    elif version < Version('2.4'):
      url = 'http://docs.python.org/ftp/python/doc/%s/html-%s.tgz' % (version, version)
    # pre 2.6
    elif version < Version('2.6'):
      url = 'http://docs.python.org/ftp/python/doc/%s/html-%s.tar.bz2' % (version, version)
    # after 2.6
    else:
      url = 'http://docs.python.org/ftp/python/doc/%s/python-%s-docs-html.tar.bz2' % (version, version)
    ret = self.shell('wget %s -O file' % url)
    if ret[0] == 0:
      if self.shell('tar xf file')[0] == 0:
        self.shell('rm file')
        ret = os.listdir('.')
        self.popd()
        if len(ret) == 1:
          return os.path.join(self.source_dir, ret[0])
        else:
          return self.source_dir
    self.popd()
