# -*- coding: utf-8 -*-
"""
Managers of ``blog`` application.
"""
from django.db import models

class CategoryOnlineManager(models.Manager):
    """
    Manager that manages online ``Category`` objects.
    """

    def get_query_set(self):
        from models import CoopEntry
        entry_status = CoopEntry.STATUS_ONLINE
        return super(CategoryOnlineManager, self).get_query_set().filter(
            entries__status=entry_status).distinct()

class EntryOnlineManager(models.Manager):
    """
    Manager that manages online ``CoopEntry`` objects.
    """

    def get_query_set(self):
        return super(EntryOnlineManager, self).get_query_set().filter(
            status=self.model.STATUS_ONLINE)
