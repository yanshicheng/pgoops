import django_filters

from apps.pgo_iac.models import Task, TaskPeriodic


class TaskFilter(django_filters.FilterSet):
    # 指定区间过滤
    """Filter for Books by if books are published or not"""
    from_periodic = django_filters.CharFilter(
        field_name="from_periodic",
    )
    from_periodic_null = django_filters.CharFilter(
        field_name="from_periodic", method="filter_from_periodic_null"
    )
    name = django_filters.CharFilter(field_name="name")

    def filter_from_periodic_null(self, queryset, name, value):
        lookup = "__".join([name, "isnull"])
        if not value:
            return queryset
        elif value == "false":
            # return queryset.filter(published_on__isnull=False)
            return queryset.filter(**{lookup: False})
        else:
            return queryset.filter(**{lookup: True})

    class Meta:
        model = Task
        fields = ["from_periodic", "name", "from_periodic_null", "state", "repository"]


class TaskPeriodicFilter(django_filters.FilterSet):
    # 指定区间过滤
    """Filter for Books by if books are published or not"""

    periodic_method = django_filters.CharFilter(
        field_name="crontab", method="filter_periodic_method"
    )
    name = django_filters.CharFilter(field_name="name")

    def filter_periodic_method(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = "__".join([name, "isnull"])
        if not value:
            return queryset
        elif value == "false":
            return queryset.filter(**{lookup: True})
        else:
            return queryset.filter(**{lookup: False})

    class Meta:
        model = TaskPeriodic
        fields = ["periodic_method", "name", "enabled", "repository"]
