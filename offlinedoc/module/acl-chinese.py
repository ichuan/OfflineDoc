#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'acl-chinese'
  homepage = 'http://acl.readthedocs.org/'
  url = 'https://github.com/acl-translation/acl-chinese'
  versioning = 'latest'

  def _new_versions(self, cur_ver):
    commits = self.github_api_get('https://api.github.com/repos/%(owner)s/%(repo)s/commits?per_page=1')
    if commits and len(commits):
      ver = Version(commits[0]['commit']['committer']['date'][:10].replace('-', ''))
      if ver > cur_ver:
        return ver

  def post_update(self, version, ret=None):
    '''
    返回最终 html 文档的路径
    '''
    self.shell('make dirhtml')
    return os.path.join(os.getcwd(), '_build/dirhtml')
