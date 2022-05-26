import multiprocessing

bind = "0.0.0.0:8000"  # 绑定ip和端口号
backlog = 1024  # 监听队列
# gunicorn要切换到的目的工作目录
chdir = "/data/ops/pgoops"
timeout = 60  # 超时
# 使用gevent模式，还可以使用sync 模式，默认的是sync模式
worker_class = "eventlet"
# 进程数
workers = multiprocessing.cpu_count() * 2 + 1
# 指定每个进程开启的线程数
threads = 2
worker_connections = 2000
# 设置进程文件目录
pidfile = "./run/pgoops_server.pid"
loglevel = "info"  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "./logs/server/pgoops_server_access.log"  # 访问日志文件
errorlog = "./logs/server/pgoops_server_error.log"  # 错误日志文件
