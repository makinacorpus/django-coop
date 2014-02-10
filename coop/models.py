# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
import shortuuid


class TimestampedModel(models.Model):
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)

    class Meta:
        abstract = True


class StaticURIModel(models.Model):
    class Meta:
        abstract = True

    active = models.BooleanField(_(u'show on public site'), default=True,)
    uuid = models.CharField(_(u'uuid'), max_length=50, null=True, editable=False, default=shortuuid.uuid)

    def label(self):
        return "Not Yet Implemented label method"


class URIModel(StaticURIModel, TimestampedModel):
    class Meta:
        abstract = True
