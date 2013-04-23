# -*- coding:utf-8 -*-
from django.conf import settings


if 'haystack' in settings.INSTALLED_APPS:
    from haystack.forms import SearchForm


    class SiteSearchForm(SearchForm):

        def set_site(self, site):
            self.site = site

        def search(self):
            # First, store the SearchQuerySet received from other processing.
            sqs = super(SiteSearchForm, self).search()
            sqs = sqs.filter(sites__contains=self.site.domain)

            return sqs


