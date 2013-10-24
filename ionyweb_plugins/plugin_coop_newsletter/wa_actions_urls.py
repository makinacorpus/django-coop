# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from ionyweb.administration.actions.utils import get_actions_urls

from models import GuestNewsletter
from forms import GuestNewsletterForm

# Generic Action View
urlpatterns = get_actions_urls(GuestNewsletter,
                               form_class=GuestNewsletterForm)