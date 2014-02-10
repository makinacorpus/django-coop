# -*- coding:utf-8 -*-
from django.conf import settings
from django.template import loader, Context


if 'haystack' in settings.INSTALLED_APPS:
    import logging
    from haystack import indexes
    from coop_local.models import Organization, Event
    from django.contrib.sites.models import Site

    log = logging.getLogger('coop')

    if getattr(settings, 'HAYSTACK_REALTIME', False):
        Indexes = indexes.RealTimeSearchIndex
    else:
        Indexes = indexes.SearchIndex


    def prepare_template(obj):
        template_names = ['search/indexes/%s/%s_rendered.txt' % (obj._meta.app_label, obj._meta.module_name)]
        t = loader.select_template(template_names)
        return t.render(Context({'object': obj, 'region_slug': settings.REGION_SLUG}))


    # The main class
    class CoopIndex(Indexes):
        text = indexes.CharField(document=True, use_template=True)
        tags = indexes.MultiValueField(boost=1.2, faceted=True)
        # modified = indexes.DateField(model_attr='modified', faceted=True)
        rendered = indexes.CharField(use_template=True, indexed=False)
        rendered.prepare_template = prepare_template

        def prepare_tags(self, obj):
            if hasattr(obj, 'tags'):
                return [u"%s" % tag.name for tag in obj.tags.all()]
            else:
                return ""

        def prepare(self, obj):
            #log.debug("prepare id=%s %s" % (obj.id, obj))
            prepared_data = super(CoopIndex, self).prepare(obj)

            prepared_data['text'] = prepared_data['text'] + ' ' + \
            ' '.join(prepared_data['tags']) 
            #log.debug("prepare text=%s" % prepared_data['text'])
            return prepared_data



    class OrganizationIndex(CoopIndex):

        def get_model(self):
            return Organization


    class EventIndex(CoopIndex):

        def get_model(self):
            return Event







