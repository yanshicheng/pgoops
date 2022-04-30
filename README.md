# Super 运维平台

[![python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://github.com/yanshicheng/super_ops)
[![django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://github.com/yanshicheng/super_ops)
[![django](https://img.shields.io/badge/django_rest_framework-Latest-green.svg)](https://github.com/yanshicheng/super_ops)
[![mysql](https://img.shields.io/badge/Mysql-5.7+-green.svg)](https://github.com/yanshicheng/super_ops)

## 简介

​	Super 开源运维平台, 主要针对复杂的, 需求不一的业务环境, 构建一套兼容性比较强的运维自动化平台.

​	平台后端使用:`django + drf`, 平台前端使用:`vue-element-admin` 进行二次开发.

## 演示地址

- **地址:** http://demo.superops.top/
- 用户名 & 密码

```bash
普通用户
	edit & edit
管理员
	super & super
```

## 地址

- [ 🌐 码云仓库后端地址](https://gitee.com/super-ops/super_ops)
- [ 🌐 码云仓库前端地址](https://gitee.com/super-ops/super_ops_web)

- [ 🌐 github仓库后端地址](https://github.com/yanshicheng/super_ops)
- [ 🌐 github仓库前端地址](https://github.com/yanshicheng/super_ops_web)

## 模块说明

- [x] 用户管理
- [x] 权限系统
  - [x] API 权限(`采用Casbin`)
  - [x] 动态菜单
- [x] 服务树
  - [ ] 陆续优化
- [x] CMDB
  - [x] 前端 + 后端
  - [x] 日志记录
  - [x] Agent API
  - [ ] Agent
- [ ] 作业平台 
  - [ ] 已完成`ansible`版本正在重构.
- [ ] 消息中心
- [ ] 调度平台
- [ ] 发布平台
- [ ] 监控配置中心

## 项目部署

- 项目代码克隆

```bash
~]# cd /opt/
~]# git clone git@gitee.com:super-ops/super_ops.git
```

- 虚拟环境准备

```bash
~]# mkdir -pv /data/venv/
~]# cd /data/venv/
~]# python3 -m venv super_ops
~]# pip install --upgrade pip -i http://pypi.douban.com/simple/
~]# pip install -r /opt/super_ops/requirements.txt  -i http://pypi.douban.com/simple/
```

- uwsgi文件修改

```bash
~]# cd /opt/super_ops/
~]# cat uwsgi.ini 
[uwsgi]
chdir           = /opt/super_ops				# 项目目录路径
module          = super_ops.wsgi
home            = /data/venv/super-ops			# 虚拟环境目录
master          = true
processes       = 4
threads         = 2
socket          = 0.0.0.0:9000
vacuum          = true
pidfile         = ./run/super_ops.pid
daemonize       = ./logs/uwsgi.log
max-requests    = 5000
touch-reload    = .git/index
```

- MYSQL地址修改

```bash
~]# cat config/config.ini
[DEFAULT]


[mysql.prod]
MYSQL_HOST = 127.0.0.1			# mysql 地址
MYSQL_PORT = 3306				# mysql 端口号
MYSQL_DB = super_ops			# msyql 数据库
MYSQL_USER = root				# mysql 用户名
MYSQL_PASSWORD = 123456			# mysql 用户密码
MYSQL_CHARSET = utf8mb4			# 字符集
MYSQL_UNIX_SOCKET = ""			# unix_socket 方式连接 mysql
```

- SQL 导入

**方式1**

​	导入现有 msyql 数据, 现有sql录入了一些数据,包括URL, 菜单权限等

```bash
mysqldump -uroot -p123456 super_ops < /ops/super_ops/super_ops.sql 
```

**方式2**

​	也可直接初始化, 但是要手动录入, 权限URL, 动态菜单等数据.

```bash
make migrate 
```

- 创建管理员

```bash
python manage.py createsuperuser
```

- 修改API超级管理员

  修改 `r.sub == "devops"` 为: `r.sub == "用户名"`

  多个超级用户可以使用 `||` 在文件末尾进行追加.

```bash
~]# cat config/prem_model.conf 
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m =  g(r.sub, p.sub) && keyMatch2(r.obj, p.obj) && ( p.act == "*" || regexMatch(r.act, p.act)) || r.sub == "devops"
```

- 启动项目

  默认访问端口: `0.0.0.0:9999`

```bash
bash start.sh
```

## 鸣谢

| 项目 |
| -------------------------------------------------- |
| [vue](https://github.com/vuejs/vue) |
| [element-ui](https://github.com/ElemeFE/element) |
| [vue-element-admin](https://panjiachen.github.io/vue-element-admin-site/zh/) |
| [axios](https://github.com/axios/axios) |

## License

[MIT](https://gitee.com/super-ops/super_ops/blob/master/LICENSE)