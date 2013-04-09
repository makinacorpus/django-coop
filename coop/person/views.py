# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from coop_local.models import Organization, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse

if 'coop_cms' in settings.INSTALLED_APPS:
    from coop_local.models import Article



def public_profile(request, uuid):
    context = {}
    person = get_object_or_404(Person, uuid=uuid, sites__id=settings.SITE_ID)
    context['person'] = person
    if 'coop_cms' in settings.INSTALLED_APPS:
        context['articles'] = Article.objects.filter(person=person).order_by('-created')

    return render_to_response('person/public_profile.html', context, RequestContext(request))
