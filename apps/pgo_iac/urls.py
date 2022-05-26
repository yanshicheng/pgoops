from rest_framework.routers import DefaultRouter
from .views.repository import RepositoryModelViewSet
from .views.task import TaskModelViewSet
from .views.task_stat import TaskStatsModelViewSet
from .views.task_event import TaskEventModelViewSet
from .views.task_periodic import TaskPeriodicModelViewSet

router = DefaultRouter()
router.register(r"v1/iac/repository", RepositoryModelViewSet)
router.register(r"v1/iac/task", TaskModelViewSet)
router.register(r"v1/iac/task-stats", TaskStatsModelViewSet)
router.register(r"v1/iac/task-event", TaskEventModelViewSet)
router.register(r"v1/iac/task-periodic", TaskPeriodicModelViewSet)

urlpatterns = []
urlpatterns += router.urls
