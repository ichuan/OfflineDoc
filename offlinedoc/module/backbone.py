#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import os
import re
from offlinedoc.module._base import GitModule, Version


class Module(GitModule):
  '''
  '''
  name = 'backbone'
  homepage = 'http://backbonejs.org/'
  url = 'https://github.com/jashkenas/backbone/'
  version_by = 'tags'
