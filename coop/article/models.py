# -*- coding:utf-8 -*-

from django.conf import settings
from coop.models import StaticURIModel, URIModel
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
import rdflib


# ----------- Customizing coop-cms Article for more coop intergration

if "coop_cms" in settings.INSTALLED_APPS:

    from coop_cms.models import BaseArticle, BaseNavTree

    class CoopArticle(BaseArticle, StaticURIModel):

        organization = models.ForeignKey('coop_local.Organization', blank=True, null=True,
                                verbose_name=_('publisher'), related_name='articles')
        person = models.ForeignKey('coop_local.Person', blank=True, null=True,
                                    verbose_name=_(u'person'), related_name='articles')

        remote_person_uri = models.CharField(_(u'person URI'), blank=True, max_length=200, editable=False)
        remote_person_label = models.CharField(_('person'), blank=True, max_length=250)

        remote_organization_uri = models.CharField(_(u'organization URI'), blank=True, max_length=200, editable=False)
        remote_organization_label = models.CharField(_('organization'), blank=True, max_length=250)

        if "coop.agenda" in settings.INSTALLED_APPS:
            dated = generic.GenericRelation('coop_local.Dated')

        def label(self):
            return self.title

        # def can_publish_article(self, user):
        #     return (self.author == user)

        #def can_edit_article(self, user):
        #   return True
        #   test on URI, not on django user

        class Meta:
            verbose_name = _(u"article")
            verbose_name_plural = _(u"articles")
            abstract = True
            app_label = 'coop_local'


        # RDF stufs
        rdf_type = settings.NS.dct.Text
        rdf_mapping = (
            ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.title, 'title'), 'single_reverse'),
            # ('single_mapping', (settings.NS.dct.abstract, 'summary'), 'single_reverse'),  # bug in rdflib
            ('single_mapping', (rdflib.term.URIRef(str(settings.NS['dct']) + 'abstract'), 'summary'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.description, 'content'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.creator, 'person'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.publisher, 'organization'), 'single_reverse'),

            ('multi_mapping', (settings.NS.dct.subject, 'tags'), 'multi_reverse'),

        )







# ----------- Idem for coop-cms NavTree            

    class CoopNavTree(BaseNavTree, URIModel):

        class Meta:
            verbose_name = _(u'Navigation tree')
            verbose_name_plural = _(u'Navigation trees')
            abstract = True
            app_label = 'coop_local'

        # RDF stuffs

        # As the "default" NavTree should NOT be exort as rdf data
        # A Nice solution is overwritte toRdfGraph method
        def toRdfGraph(self):
            g = rdflib.ConjunctiveGraph()
            if not self.name == 'default':
                g.add((rdflib.term.URIRef(self.uri), settings.NS.rdf.type, self.rdf_type))
                for method, arguments, reverse in self.rdf_mapping:
                    for triple in getattr(self, method)(*arguments):
                        g.add(triple)
            return g

        rdf_type = settings.NS.skos.ConceptScheme
        rdf_mapping = (
            ('single_mapping', (settings.NS.dct.created, 'created'), 'single_reverse'),
            ('single_mapping', (settings.NS.dct.modified, 'modified'), 'single_reverse'),
            ('single_mapping', (settings.NS.rdfs.label, 'name'), 'single_reverse'),
        )


    



