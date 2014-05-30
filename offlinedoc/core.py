#!/usr/bin/env python
# coding: utf-8
# yc@2013/05/10

import os, logging, yaml, sys, imp, glob, datetime
from module._base import Version
from jinja2 import Environment, FileSystemLoader


OD_DIR = os.path.dirname(os.path.abspath(__file__))
now = datetime.datetime.utcnow

class OfflineDoc(object):
  '''
  '''
  def __init__(self, data_dir=None):
    self.module_counter = 0
    self.setup_logger()
    self.data_dir = data_dir
    self.config = {}
    if data_dir:
      self.file_config = os.path.join(data_dir, 'config.yaml')
      self.load_config()
      self.load_jinja2()

  def setup_logger(self):
    '''
    注册 logger，会被自身和各 module 使用
    输出到标准输出
    '''
    logger = logging.getLogger('offline-doc')
    handler = logging.StreamHandler()
    handler.setFormatter(
      logging.Formatter('[%(asctime)s]-%(levelname)s: %(message)s')
    )
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    self.logger = logger

  def load_jinja2(self):
    theme = self.config.get('theme', 'simple')
    self.jinja_env = Environment(loader=FileSystemLoader([
      os.path.join(OD_DIR, 'theme', theme),
      os.path.join(self.data_dir, 'theme', theme)
    ]))

  def load_config(self):
    try:
      self.config = yaml.safe_load(open(self.file_config))
      assert isinstance(self.config, dict)
    except Exception, e:
      self.logger.error('Cannot load config: %s' % e)

  def save_config(self):
    try:
      with open(self.file_config, 'w+') as fp:
        fp.write(yaml.safe_dump(self.config))
    except Exception, e:
      self.logger.error('Cannot save config: %s' % e)

  def load_modules(self, force=False):
    if force or not getattr(self, 'modules', None):
      self.modules = {}
      # 1. builtins
      self._load_from_dir(OD_DIR)
      # 2. customs
      if self.data_dir:
        self._load_from_dir(self.data_dir)
    return self.modules

  def _load_from_dir(self, module_dir):
    for path in glob.glob(os.path.join(module_dir, 'module', '*.py')):
      if not os.path.basename(path).startswith('_'):
        self._load_module(path)

  def _load_module(self, path):
    try:
      m = imp.load_source('_odm_%d' % self.module_counter, path)
      name = m.Module.name
      if name in self.modules:
        self.logger.error('Module %s exists, failed loading %s' % (name, path))
      else:
        self.module_counter += 1
        self.modules[name] = m.Module
    except Exception, e:
      self.logger.warn('Cannot load module from %s: %s' % (path, e))

  def get_module(self, name):
    '''
    get module instance
    '''
    if not hasattr(self, '_instances'):
      self._instances = {}
    if not name in self._instances:
      self._instances[name] = self.modules[name](
        self.data_dir,
        self.config,
        self.jinja_env.get_template('module.html')
      )
    return self._instances[name]

  def get_latest_version(self, name):
    '''
    get latest version of a module
    '''
    return self.config.get('versions', {}).get(name, {}).get('latest')

  def update(self, name=None, version=None):
    '''
    '''
    modules = self.load_modules()
    if name:
      if not name in modules:
        self.logger.error('Module %s not exist' % name)
        return False
      modules = {name: modules[name]}
    for key in modules:
      self.logger.info('Checking %s ...', key)
      obj = self.get_module(key)
      versions = [Version(version)] if version else obj.new_versions()
      if versions:
        for ver in versions:
          self.logger.info('Updating %s %s ...', key, ver)
          attrs = obj.do_update(ver)
          if attrs:
            self.config['versions'][key] = attrs
            self.config['last_update'] = now()
            self.save_config()
    self.generate_index()
    self.logger.info('All modules updated')

  def generate_index(self):
    '''
    生成 modules 索引
    '''
    tpl_index = self.jinja_env.get_template('index.html')
    modules = self.load_modules().keys()
    for i in modules:
      self.get_module(i).generate_index()
    last_update = self.config.get('last_update', now())
    html = tpl_index.render({'modules': modules, 'last_update': last_update})
    open(os.path.join(self.data_dir, 'public', 'index.html'), 'w+').write(html)
