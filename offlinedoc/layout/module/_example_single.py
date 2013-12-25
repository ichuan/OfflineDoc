#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

'''
文档只有单一 HTML 文件的模块，只抓取一次
'''

import os
import re
from offlinedoc.module._base import SingleHtmlModule


class Module(SingleHtmlModule):
  '''
  '''
  # 唯一 id（格式要求同 Linux 文件名）
  name = 'sed'
  # 版本类型
  #   normal: 递增，保留所有版本（例如：bootstrap）
  #   latest: 递增，只保留最新版本（例如：jquery）
  #   single: 只抓取一次，无论新旧（例如：sed）
  versioning = 'single'
  # 由于只抓取一次，可以直接给出版本号。否则需要定义 _new_versions() 函数
  version = '4.2.1'
  # 文档地址
  url = 'http://www.gnu.org/software/sed/manual/sed.html'
