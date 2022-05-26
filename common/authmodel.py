from django.contrib.auth import get_user_model
from django.db import models


class AuthorModelMixin(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
