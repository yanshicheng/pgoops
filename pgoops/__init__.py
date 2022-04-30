import pymysql
from .celery import pgoops_celery_app as celery_app
# celery_app.autodiscover_tasks(
#     [
#         "apps.pgo_message_center",
#     ],
# )
__all__ = (celery_app,)
pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()
