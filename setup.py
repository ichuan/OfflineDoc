#!/usr/bin/env python
# coding: utf-8
# yc@2013/12/03

import os
from distutils.core import setup

setup(
  name='OfflineDoc',
  version='0.0.7',
  author='yc',
  author_email='iyanchuan@gmail.com',
  packages=['offlinedoc', 'offlinedoc.test', 'offlinedoc.module'],
  package_data={'offlinedoc': [
    'layout/*.yaml', 'layout/module/*.py', 'layout/public/.*', 'layout/source/.*',
    'layout/theme/.*', 'theme/*/*',
  ]}, # see http://stackoverflow.com/a/7414693/265989
  scripts=['bin/od.py'],
  url='https://github.com/ichuan/OfflineDoc',
  license='LICENSE.txt',
  description='Offline documents generating tool',
  long_description=open('README.txt').read(),
  install_requires=[
    'Jinja2==2.6',
    'PyYAML==3.10',
    'Pygments==1.6',
    'Sphinx==1.1.3',
    'docutils==0.10',
    'rst2pdf>0.92',
    'sphinx-bootstrap-theme==0.3.4',
    'jsonschema==2.3.0',
  ]
)
