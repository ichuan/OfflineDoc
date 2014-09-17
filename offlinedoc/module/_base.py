#!/usr/bin/env python
# coding: utf-8
# yc@2013/03/20

import sys, os, json, subprocess, urllib2, urlparse, logging, logging.handlers
import subprocess, shutil, re
from threading import Lock
from itertools import izip_longest
from contextlib import contextmanager

RE_GITHUB_URL = re.compile(r'https?://github.com/(?P<user>[^/]+)/(?P<repo>[^/]+)')
RE_SLUG = re.compile(r'^([\d\.]+)(.*)$')


class Version(str):
  '''
  semver https://github.com/mojombo/semver
  '''
  def __init__(self, ver):
    super(Version, self).__init__(ver)
    try:
      self._vers = map(int, ver.split('.'))
    except:
      # fallback to normal string
      pass

  def __cmp__(self, other):
    if not hasattr(self, '_vers') or not hasattr(other, '_vers'):
      # slug match
      try:
        a1, b1 = re.match(RE_SLUG, self).groups()
        a2, b2 = re.match(RE_SLUG, other).groups()
        a1, a2 = a1.rstrip('.'), a2.rstrip('.')
        b1, b2 = b1.lstrip('.-'), b2.lstrip('.-')
        ret = cmp(Version(a1), Version(a2))
        if ret == 0:
          # 2.7.rc2 > 2.7.rc1
          if b1 and b2:
            return cmp(b1, b2)
          # 2.7 > 2.7.rc1
          return 1 if b2 else -1
        # 2.7.1.rc2 > 2.7
        return ret
      except:
        # beta > alpha
        return cmp(str(self), str(other))

    for i, j in izip_longest(self._vers, other._vers, fillvalue=0):
      result = i - j
      if result != 0:
        return result
    return 0

  __lt__ = __le__ = __eq__ = __ne__ = __gt__ = __ge__ = \
    lambda *i : NotImplemented


class BaseModule(object):
  '''
  '''
  # 唯一 id
  name = '_module_'
  # 主页，获取 favicon 用
  homepage = None
  # 版本类型
  #   normal: 递增，保留所有版本（bootstrap）
  #   latest: 递增，只保留最新版本（jquery）
  #   single: 只抓取一次，无论新旧（sed）
  versioning = 'normal'

  def __init__(self, data_dir, config=None, tpl=None):
    '''
    attrs: {latest: None, versions: []}
    '''
    assert self.versioning in ('normal', 'latest', 'single'), 'versioning error'
    self.dir_stack = []
    self.config = config
    self.tpl = tpl
    self.logger = logging.getLogger('offline-doc')
    self.attrs = config['versions'].get(self.name) or {'latest': None, 'versions': []}
    self.source_dir = os.path.join(data_dir, 'source', self.name)
    self.public_dir = os.path.join(data_dir, 'public', self.name)
    [os.makedirs(i) for i in (self.source_dir, self.public_dir) if not os.path.isdir(i)]
    self.init()

  def init(self):
    '''
    subclass init
    '''
    pass

  def __str__(self):
    return self.name

  def shell(self, cmd):
    '''
    run command in shell and return status and output
    '''
    pipe = subprocess.PIPE
    if os.environ.get('ODDEBUG'):
      stdout = sys.stdout
      stderr = sys.stderr
    # TODO bug: when ODDEBUG=1, stdout && stderr is None
    exe = subprocess.Popen(cmd, stdout=pipe, stderr=pipe, shell=True)
    if os.environ.get('ODDEBUG'):
      print ' *', cmd
      out, err = [], []
      while exe.poll() is None:
        m = exe.stdout.readline()
        n = exe.stderr.readline()
        sys.stdout.write(m)
        sys.stderr.write(n)
        out.append(m)
        err.append(n)
      out = ''.join(out)
      err = ''.join(err)
    else:
      out, err = exe.communicate()

    if exe.returncode != 0:
      self.logger.warn('Command failed: \n>>> %s\n%s %s%s' % (cmd, exe.returncode, out, err))
    return exe.returncode, '%s%s' % (out, err)

  def pushd(self, path):
    '''
    like pushd / popd in shell
    '''
    self.dir_stack.append(os.getcwd())
    os.chdir(path)

  def popd(self):
    os.chdir(self.dir_stack.pop())

  def http_get(self, url, jsonret=False, basic_auth=False, suppress_error=False):
    '''
    curl
    '''
    try:
      req = urllib2.Request(url)
      if basic_auth:
        req.add_header('Authorization', 'Basic %s' % basic_auth)
      fp = urllib2.urlopen(req)
      if jsonret:
        return json.load(fp)
      return fp.read()
    except Exception, e:
      if not suppress_error:
        self.logger.warn('http_get error: %s => %s' % (url, e))
    return False

  def github_api_get(self, url):
    '''
    auto transform "/repos/%(owner)s/%(repo)s/commits" to "/repos/github/docfiles/commits"
    '''
    if not self.config.get('github_auth'):
      self.logger.warn('Github Account not specified, aborted. Use `od.py auth <dir>` to add github account first.')
      return []
    obj = RE_GITHUB_URL.search(self.url)
    if obj:
      user = obj.group('user')
      repo = obj.group('repo')
      if repo.endswith('.git'):
        repo = repo[:-4]
      url = url % {'owner': user, 'repo': repo}
    return self.http_get(url, jsonret=True, basic_auth=self.config.get('github_auth', ''))

  def yql_get(self, url):
    '''
    YQL query result
    '''
    ret = self.http_get(url, jsonret=True)
    if ret and 'query' in ret and 'results' in ret['query'] and \
      ret['query']['results']:
      return ret['query']['results']
    self.logger.warn('yql_get error: %s', ret)

  def wget_mirror(self, url, output_dir, **kwargs):
    '''
    wget 镜像一个站点
    '''
    kwargs['mirror'] = None
    return self.wget(url, output_dir, **kwargs)

  def wget(self, url, output_dir, **kwargs):
    cmd = ('wget --tries=3 --user-agent=msie --execute robots=off '
      '--convert-links --no-host-directories --adjust-extension '
      '--no-check-certificate --timeout=60 --page-requisites '
      '--no-cookies --no-parent -o /dev/null ')
    for i, j in kwargs.items():
      if j is not None:
        cmd += '--%s=%s ' % (i, j)
      else:
        cmd += '--%s ' % i
    cmd += url
    try:
      self.pushd(output_dir)
      return self.shell(cmd)
    finally:
      self.popd()

  def save_favicon(self):
    if not self.homepage and hasattr(self, 'url'):
      self.homepage = urlparse.urlparse(self.url).netloc
    if not self.homepage or getattr(self, 'fetched_favicon', False):
      return
    self.fetched_favicon = True
    api = 'http://www.google.com/s2/favicons?domain_url=' + self.homepage
    save_as = os.path.join(self.public_dir, 'favicon.png')
    try:
      open(save_as, 'wb+').write(self.http_get(api))
    except:
      pass

  def clear_source(self):
    try:
      shutil.rmtree(self.source_dir)
      os.makedirs(self.source_dir)
    except OSError, e:
      self.logger.warn('clear_source error: %s' % e)

  def clear_public(self):
    try:
      shutil.rmtree(self.public_dir)
      os.makedirs(self.public_dir)
    except OSError, e:
      self.logger.warn('clear_public error: %s' % e)

  def entry(self, version):
    '''
    文档入口页（index.html 或者 docs/a.html 等）
    '''
    return ''

  def generate_index(self):
    if self.attrs['latest'] is None:
      return
    context = {
      'name': self.name,
      'latest': {
        'version': self.attrs['latest'],
        'entry': '%s/%s' % (self.attrs['latest'], self.entry(self.attrs['latest'])),
      },
      'versions': [],
    }
    for i in sorted((Version(i) for i in self.attrs['versions']), reverse=True):
      context['versions'].append({
        'version': str(i),
        'entry': '%s/%s' % (i, self.entry(i)),
      })
    html = self.tpl.render(context)
    open(os.path.join(self.public_dir, 'index.html'), 'w+').write(html)


  def pre_update(self, version):
    '''
    根据返回值判断是否需要更新
    '''
    return True

  def post_update(self, version, ret=None):
    '''
    should return a path containing generated html
    '''
    return self.source_dir

  @contextmanager
  def _update(self, version=None):
    '''
    更新操作迭代器，用来下载文件、更新仓库。被 do_update 使用
    '''
    yield

  def do_update(self, version):
    '''
    update a specific version, return new attrs
    '''
    if not self.pre_update(version):
      self.logger.error('pre_update not satisfied, not updated')
      return
    try:
      with self._update(version) as ret:
        download_dir = self.post_update(version, ret)
    except Exception, e:
      self.logger.error('update error: %s' % e)
      return

    self.save_favicon()
    if download_dir:
      if self.versioning == 'latest':
        self.clear_public()
      dst_dir = os.path.join(self.public_dir, version)
      try:
        shutil.rmtree(dst_dir)
      except OSError:
        pass
      try:
        shutil.copytree(download_dir, dst_dir, ignore=shutil.ignore_patterns('.git', '.svn'))
        ver_str = str(version)
        if self.versioning == 'latest':
          self.attrs['latest'] = ver_str
          self.attrs['versions'] = [ver_str]
        else:
          if not ver_str in self.attrs['versions']:
            self.attrs['versions'].append(ver_str)
          self.attrs['latest'] = str(max(Version(i) for i in self.attrs['versions']))
        self.generate_index()
        return self.attrs
      except OSError, e:
        self.logger.error('Cannot copy dir: %s => %s (%s)' % (download_dir, \
                          dst_dir, e))
    else:
      self.logger.error('post_update faild: ' + self.name)

  def new_versions(self):
    '''
    无须更新时返回 False
    需要更新时返回版本列表
    '''
    if self.versioning == 'single':
      if self.attrs['latest']:
        return False
      if hasattr(self, 'version'):
        return [Version(self.version)]
    ret = self._new_versions(Version(self.attrs['latest'] or '0'))
    if isinstance(ret, Version):
      ret = [ret]
    if ret and self.versioning == 'latest':
      ret = [max(ret)]
    return ret

  def _new_versions(self, cur_ver):
    '''
    返回比 cur_ver 还新的版本或版本列表
    '''
    raise NotImplementedError


class GitModule(BaseModule):
  '''
  '''
  url = 'http://github.com/mongodb/docs.git'
  _updated_repo = False
  # 以什么做为版本标识，releases 或 tags
  version_by = 'releases'
  # tag 字段名
  tag_field = 'tag_name'

  def __init__(self, *a, **b):
    assert self.version_by in ('releases', 'tags'), 'version_by error'
    if self.version_by == 'tags':
      self.tag_field = 'name'
    super(GitModule, self).__init__(*a, **b)

  def post_update(self, version, ret=None):
    return os.path.join(self.source_dir, 'docs')

  @contextmanager
  def _update(self, version=None):
    '''
    '''
    self.pushd(self.source_dir)
    if not os.path.isdir('docs'):
      self.logger.info('Cloning git repo ...')
      self.shell('git clone %s docs' % self.url)
      self.pushd('docs')
      self._updated_repo = True
    else:
      self.logger.info('Updating git repo ...')
      self.pushd('docs')
      self.shell('rm -f .gitignore') # for git-clean to work
      self.shell('git clean -f -d')
      self.shell('git reset --hard HEAD')
      if not self._updated_repo:
        self.shell('git checkout master && git pull')
        self._updated_repo = True
      out = self.shell('git tag | tail -1')[1].strip()
      if out:
        tag_prefix = 'v' if out.startswith('v') else ''
        self.shell('git checkout %s%s' % (tag_prefix, version))
    # 当前目录：git 目录
    self.logger.info('Building ...')
    yield
    self.popd()
    self.popd()

  def _new_versions(self, cur_ver):
    '''
    是否 github，github 会按 releases/tags 作版本
    '''
    result = self.github_api_get(
      'https://api.github.com/repos/%%(owner)s/%%(repo)s/%s?per_page=100'
      % self.version_by
    )
    if result:
      tags = (i[self.tag_field].lstrip('v') for i in result)
      sorted_versions = sorted(Version(i) for i in tags)
      return [i for i in sorted_versions if i > cur_ver]
    raise NotImplementedError


class SvnModule(BaseModule):
  '''
  '''
  url = ''

  @contextmanager
  def _update(self, version=None):
    '''
    '''
    self.pushd(self.source_dir)
    if not os.path.isdir('docs'):
      self.logger.info('Cloning svn repo ...')
      self.shell('svn co %s docs' % self.url)
      self.pushd('docs')
    else:
      self.logger.info('Updating svn repo ...')
      self.pushd('docs')
      self.shell('svn cleanup')
      self.shell('svn revert -R . && svn up')
    self.logger.info('Building ...')
    yield
    self.popd()
    self.popd()


class SingleHtmlModule(BaseModule):
  '''
  '''
  versioning = 'single'
  url = ''

  def entry(self, version):
    return os.path.basename(
      os.path.normpath(
        urlparse.urlparse(self.url).path
      )
    )

  @contextmanager
  def _update(self, version=None):
    self.clear_source()
    parsed = urlparse.urlparse(self.url)
    path = os.path.normpath(parsed.path)
    options = {'cut-dirs': path.count('/') - 1, 'domains': parsed.netloc}
    ret = self.wget(self.url, self.source_dir, **options)
    yield ret

  def post_update(self, version, ret):
    if ret[0] in (0, 8):
      return self.source_dir

