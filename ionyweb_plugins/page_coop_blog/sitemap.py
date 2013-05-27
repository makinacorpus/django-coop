# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap

from models import CoopEntry

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def __init__(self, blog=None, *args, **kwargs):
        super(BlogSitemap, self).__init__(*args, **kwargs)
        if blog:
            self.queryset = CoopEntry.objects.filter(blog=blog, status=CoopEntry.STATUS_ONLINE).order_by('-publication_date')
        else:
            self.queryset = CoopEntry.objects.filter(status=CoopEntry.STATUS_ONLINE).order_by('-publication_date')

    def items(self):
        return self.queryset

    def lastmod(self, obj):
        return obj.modification_date
