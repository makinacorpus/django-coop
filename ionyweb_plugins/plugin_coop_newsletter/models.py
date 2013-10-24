# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from ionyweb.plugin.models import AbstractPlugin



class Plugin_CoopNewsletter(AbstractPlugin):
    
    def __unicode__(self):
        return u'Newsletter Form #%d' % (self.pk)


    def get_admin_form(self):
        from forms import Plugin_CoopNewsletterFormAdmin
        return Plugin_CoopNewsletterFormAdmin

    class Meta:
        verbose_name = ugettext(u"Newsletter Form")

        
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