# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


from ionyweb.page.models import AbstractPageApp



class PageApp_CoopNewsletter(AbstractPageApp):
    
    # Define your fields here

    def __unicode__(self):
        return u'CoopNewsletter #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopNewsletter")


class GuestNewsletter(models.Model):
    first_name = models.CharField(_(u'First name'),
                                       max_length=50,
                                       blank=True, null=True)
                                       
    last_name = models.CharField(_(u'Last name'),
                                       max_length=50,
                                       blank=True, null=True)

    email = models.EmailField(_(u'email'))
    
    def __unicode__(self):
        return u'%s' % self.email