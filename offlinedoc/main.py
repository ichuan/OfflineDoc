#!/usr/bin/env python
# coding: utf-8
# yc@2013/12/03

import os, sys, shutil, yaml, base64
import offlinedoc
from offlinedoc.core import OfflineDoc


def die(msg, test=True):
  if test:
    print msg
    sys.exit(1)


def usage(cmdpath=sys.argv[0]):
  return '''OfflineDoc: Offline documents generating tool
Usage: %(od)s <action> [arg] ...
  %(od)s new <dir>                        - create a project and place data into <dir>
  %(od)s update <dir> [module [version]]  - update a project in <dir> (optional specific module, version)
  %(od)s index <dir>                      - rebuild index html files in <dir>
  %(od)s serve <dir>                      - simple http server for <dir> (alias python -m SimpleHTTPServer)
  %(od)s clear <dir>                      - clear all data in <dir> (alias rm -rf <dir>)
  %(od)s list [dir]                       - list all modules (optional with custom modules in a dir)
  %(od)s auth <dir>                       - setup github auth for a project
  %(od)s version                          - current version
  %(od)s help                             - prints this info

Turn on debug mode:
  ODDEBUG=1 %(od)s <action> [arg] ...
''' % {'od': os.path.basename(cmdpath)}


def is_project(path):
  '''
  '''
  if not isinstance(path, str):
    return False
  file_config = os.path.join(path, 'config.yaml')
  if os.path.isfile(file_config) and \
     os.path.isdir(os.path.join(path, 'public')) and \
     os.path.isdir(os.path.join(path, 'source')):
    try:
      yaml.safe_load(open(file_config))
      return True
    except:
      pass
  return False


def cmd_new(path=None):
  '''
  create a project and place data into path
  '''
  die('Path required', path is None)
  if os.path.isdir(path):
    die('Directory %s already exists' % path, not is_project(path))
    action = 'exists'
  else:
    template_path = os.path.join(offlinedoc.__path__[0], 'layout')
    action = 'created'
    try:
      shutil.copytree(template_path, path)
    except OSError, e:
      die('Cannot create dir "%s": %s' % (path, e))
  print '''Project %(action)s, here's an example nginx config:

  server {
    listen 80;
    server_name localhost.doc;
    access_log off;
    error_log /dev/null;
    root %(public)s;
    location = /index.html { expires epoch; }
    location ~ ^/[^\/]+/index.html$ { expires epoch; }
  }
''' % {'public': os.path.join(os.path.abspath(path), 'public'), 'action': action}


def cmd_update(path=None, name=None, version=None):
  '''
  update a project in path
  '''
  die('Not a valid data dir', not is_project(path))
  od = OfflineDoc(path)
  od.update(name, version)


def cmd_index(path=None):
  die('Not a valid data dir', not is_project(path))
  od = OfflineDoc(path)
  od.generate_index()


def cmd_serve(path=None):
  die('Not a valid data dir', not is_project(path))
  os.chdir(os.path.join(path, 'public'))
  os.system('python -m SimpleHTTPServer')


def cmd_auth(path=None):
  die('Not a valid data dir', not is_project(path))
  od = OfflineDoc(path)
  user = raw_input('Enter github username: ')
  password = raw_input('Enter github password: ')
  if user and password:
    od.config['github_auth'] = base64.b64encode('%s:%s' % (user, password))
    od.save_config()
    print 'Auth saved'
  else:
    print 'Invalid inputs'


def cmd_clear(path=None):
  die('Not a valid data dir', not is_project(path))
  die('', raw_input('Are you sure to delete? [y/n]') != 'y')
  try:
    shutil.rmtree(path)
  except OSError, e:
    die('Clear data error: %s' % e)


def cmd_list(path=None):
  '''
  list modules
  '''
  od = OfflineDoc(path if is_project(path) else None)
  print 'Modules available:\n'
  for i in od.load_modules().keys():
    j = i
    if path:
      k = od.get_latest_version(i)
      if k:
        j = '%s@%s' % (j, k)
    print ' - %s' % j
  print


def exec_cli(args):
  '''
  '''
  action = None
  if len(args) > 1:
    action = args[1]

  if action in ('new', 'index', 'update', 'clear', 'list', 'auth', 'serve'):
    try:
      sys.exit(globals()['cmd_' + action](*args[2:]))
    except TypeError:
      raise

  if action == 'version':
    import pkg_resources
    print pkg_resources.require('offlinedoc')[0].version
  else:
    sys.exit(usage(args[0]))


if __name__ == '__main__':
  exec_cli(sys.argv)
