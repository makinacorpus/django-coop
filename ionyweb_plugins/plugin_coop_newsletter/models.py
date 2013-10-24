# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from ionyweb.plugin.models import AbstractPlugin



class Plugin_CoopNewsletter(AbstractPlugin):
    
    def __unicode__(self):
        return u'Newsletter Form #%d' % (self.pk)

    class Meta:
        verbose_name = ugettext(u"Newsletter Form")
        
    class ActionsAdmin:
        actions_list = (
            {'title':_(u'Edit guests'),
             'callback': "admin.plugin_coop_newsletter.edit_guests"},
            )     

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