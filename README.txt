# OfflineDoc: 离线文档生成器

## 由来

作为一个程序员，每天的工作打交道最多的除了写代码，估计就是查文档了。mongodb 有个 update modifier 又忘记格式要求了，django 的 model 都有哪些 field 类型，都得查文档。要做到高效工作，不需要背下所有知识，只需要知道什么时候该用什么东西，去哪里找需要的东西。

去哪里查文档呢？很多情况下你不会去 google，因为你知道你要找的就在**官方文档**里。所以遇到一门新语言、一个新库，我推荐的学习方式就是把官方文档大致看一遍，这样 以后遇到问题大概就会知道官方文档里有没有这方面的资料。

官方文档是最全面权威的文档，一般都是在线 HTML 页面方式呈现。我很喜欢浏览 HTML 版本的文档：不需要额外软件或插件，只需要一个浏览器；图文并茂，而且大部分前端的还在文档中自带 demo。我经常沉浸在 python、django、angular.js、pymongo 的在线文档里，收获颇丰。

看起来很好。但是，在线文档有几个致命的缺点：

1. 离线无法使用。这样你在无网络的环境下就没法查文档写代码了。
2. 龟速网络导致查文档时间大部分浪费在等待网络 I/O 上了。不可忍。
3. 大部分只提供最新版本文档，不提供历史文档。维护旧代码时查文档很痛苦。

由此出现了一些专门给程序员看的文档服务，如 http://devdocs.io/ 和 https://readthedocs.org/ 。似乎很不错，但是，这两个服务也有缺点：

devdocs.io:

1. 按自己格式排版了文档。官方文档的排版和内容才是王道。
2. 支持项目少，版本旧，增加项目困难。由于有一套排版，更新岂能不困难。

readthedocs.org:

1. 只支持有 sphinx 编写的文档的项目

这两者都有一个致命的缺点：无法灵活添加自有项目（例如公司内部项目）；无法添加诸如 amcharts 本身根本不提供文档生成方法的项目。

所以才有了 OfflineDoc 的诞生。OfflineDoc 的目标是用简单的方式去生成、定期更新离线文档，并解决上述难题。


## 介绍

OfflineDoc 支持的项目类型有：

1. Git 项目
2. SVN 项目
3. 其它有 HTML 文档的任意项目

对 Git 和 SVN 项目，OfflineDoc 会取出源码，如果该项目有自身的文档生成方法（Sphinx、jekyl、make、Rake 等），会利用相应方式生成和官方一样的 HTML 文档；对其余不提供文档生成方法的流氓项目，只要其有在线 HTML 文档，就会使用 wget 镜像大法全部抓下来。


## 使用

首先安装（推荐使用 virtualenv）：

    mkdir -p ~/envs
    virtualenv ~/envs/od
    source ~/envs/od/bin/activate
    pip install offlinedoc

最终显示 "Successfully installed ..." 之类表示正确安装了。由于内置了二十多个常用项目，在生成它们的文档前需要安装一些库（以 ubuntu 为例）：

1. nodejs：`sudo apt-get install nodejs`。或者直接去官网下载最新版本。
2. grunt 和 bower：`sudo npm install -g grunt-cli && sudo npm install bower -g`
3. 编译依赖包：`sudo apt-get install build-essential python-dev ruby1.9.1-dev git-core default-jre`
4. jekyll：`sudo gem install jekyll`

安装好之后，在 shell 下输入 `od.py` 回车看看：

    OfflineDoc: Offline documents generating tool
    Usage: od.py <action> [arg] ...
      od.py new <dir>                        - create a project and place data into <dir>
      od.py update <dir> [module [version]]  - update a project in <dir> (optional specific module, version)
      od.py index <dir>                      - rebuild index html files in <dir>
      od.py serve <dir>                      - simple http server for <dir> (alias python -m SimpleHTTPServer)
      od.py clear <dir>                      - clear all data in <dir> (alias rm -rf <dir>)
      od.py list [dir]                       - list all modules (optional with custom modules in a dir)
      od.py auth <dir>                       - setup github auth for a project
      od.py version                          - current version
      od.py help                             - prints this info

    Turn on debug mode:
      ODDEBUG=1 od.py <action> [arg] ...

普遍使用流程是这样：

1. 选择一个大分区目录用来存放离线文档，比如 `/var/data/od`，则使用 `od.py new /var/data/od` 初始化之：

    $od.py new /var/data/od
    Project created, here's an example nginx config:

      server {
        listen 80;
        server_name localhost.doc;
        access_log off;
        error_log /dev/null;
        root /var/data/od/public;
        location = /index.html { expires epoch; }
        location ~ ^/[^\/]+/index.html$ { expires epoch; }
      }

    会显示一个 nginx 配置示例，把这块加入 nginx 配置后，就可以网页浏览生成好的离线文档了。当然需要安装 nginx，不过 OfflineDoc 也有自带一个小 http 服务器供文档浏览。
2. github 认证：`od.py auth /var/data/od`。由于部分内置项目托管在 github 上，OfflineDoc 有用到 github 的 api 接口，所以需要在该数据目录中保存一个 github 账号信息。可以花一两分钟去创建一个 github 账号。
3. 开始更新：`od.py update /var/data/od`。这会把内置的二十多个项目的几乎所有版本的离线文档都生成出来，当然是比较花时间的。可以选择性生成。比如 `od.py update /var/data/od bootstrap` 会只生成 bootstrap 所有版本的文档，执行 `od.py update /var/data/od bootstrap 2.3.2` 只会生成 bootstrap 2.3.2 版本的文档。
4. 生成索引：`od.py index /var/data/od`。这步不是必须的。当你单独更新了某个项目的文档时，浏览器里没有看到变化，可以执行此命令重新生成所有项目的索引页面。
5. 浏览文档：`od.py serve /var/data/od`。这会在本机 8000 端口启动一个 http 服务，访问即可看到生成好的文档。
6. 查看目前已有项目列表及最新版本：`od.py list /var/data/od` 不加最后一个参数会只显示内置项目列表，加上会显示在那个数据目录中的版本号，而且该数据目录中的自定义项目。

如果遇到问题，可以把 `ODDEBUG=1` 加在 `od.py` 命令前面，例如：`ODDEBUG=1 od.py update /var/data/od`，这样会输出调试信息，方便排查。错误信息可以贴到 https://github.com/ichuan/OfflineDoc/issues 。

可以把更新命令放入 crontab，每日更新，这样就能时刻保持文档最新。

这里有个更新完毕后的站点供参考：http://doc.ichuan.net/


## 扩展

除了这些，OfflineDoc 还支持自定义项目和索引页面主题自定义。

关于自定义项目，可以参考生成的数据目录 /var/data/od 中的 module 目录，其中有四个示例，分别对应 git、svn、单 html 页面个需要 wget 镜像的项目。自定义模块的文件名以下划线开头的话是会被 OfflineDoc 忽略的。

关于自定义主题，可以参考 OfflineDoc 源码，同样在数据目录下的 theme 目录中添加自己的 jinja2 模板文件，OfflineDoc 生成索引时会优先使用此目录的模板文件，而非系统内置。


## 贡献

目前有下面几块需要帮忙完善：

1. 除了现在内置的二十多个，继续补充常用的文档
2. 其它主题模板（例如 bootstrap 风格等）
3. 使用，指出遇到的 bug
4. 扩展开发文档
