# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.conf import settings
from coop.models import URIModel
from coop.utils.fields import MultiSelectField

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.models import Area, Location


class BaseProduct(URIModel):
    title = models.CharField(_('title'), blank=True, max_length=250)
    slug = exfields.AutoSlugField(populate_from='title')
    description = models.TextField(_(u'description'), blank=True)
    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True, 
                                        verbose_name='publisher', related_name='products')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    uri = models.CharField(_(u'main URI'), blank=True, max_length=250, editable=False)
    publisher_uri = models.CharField(_(u'publisher URI'), blank=True, max_length=200, editable=False)

    @property
    def uri_id(self):
        return self.id
    uri_fragment = 'product'

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ['-modified']
        verbose_name = _(u'Product')
        verbose_name_plural = _(u'Products')


EWAY = Choices(
    ('OFFER',   1,  _(u"I'm offering")),
    ('NEED',    2,  _(u"I'm looking for"))
)

ETYPE = Choices(
    ('PROD',    1,  _(u'Product or Material')),
    ('SERVE',   2,  _(u'Service')),
    ('SKILL',   3,  _(u'Skill')),
    ('COOP',    4,  _(u'Partnership')),
    ('QA',      5,  _(u'Question')),
)


class BaseExchangeMethod(models.Model):  # this model will be initialized with a fixture
    label = models.CharField(_(u'label'), max_length=250)
    uri = models.CharField(_(u'URI'), blank=True, max_length=250)
    etypes = MultiSelectField(_(u'applicable to'), max_length=250, null=True, blank=True, choices=ETYPE.CHOICES)
    
    def applications(self):
        return u", ".join([ETYPE.CHOICES_DICT[int(e)].__unicode__() for e in self.etypes])
    applications.short_description = _(u'applications')
    
    def __unicode__(self):
        return self.label

    class Meta:
        abstract = True
        verbose_name = _(u'Exchange method')
        verbose_name_plural = _(u'Exchange methods')


class BaseExchange(URIModel):
    title = models.CharField(_('title'), max_length=250)
    description = models.TextField(_(u'description'), blank=True)
    organization = models.ForeignKey('coop_local.Organization', blank=True, null=True, 
                            verbose_name=_('publisher'), related_name='exchanges')
    person = models.ForeignKey('coop_local.Person', blank=True, null=True, verbose_name=_(u'person'))
    
    eway = models.PositiveSmallIntegerField(_(u'exchange way'), choices=EWAY.CHOICES, default=EWAY.OFFER)
    etype = models.PositiveSmallIntegerField(_(u'exchange type'), choices=ETYPE.CHOICES)

    permanent = models.BooleanField(_(u'permanent'), default=True)
    expiration = models.DateField(_(u'expiration'), blank=True, null=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    products = models.ManyToManyField('coop_local.Product', verbose_name=_(u'linked products'))
    uri = models.CharField(_(u'main URI'), blank=True, max_length=250, editable=False)
    author_uri = models.CharField(_(u'author URI'), blank=True, max_length=200, editable=False)
    publisher_uri = models.CharField(_(u'publisher URI'), blank=True, max_length=200, editable=False)

    methods = models.ManyToManyField('coop_local.ExchangeMethod', verbose_name=_(u'exchange methods'))

    uuid = exfields.UUIDField()  # nécessaire pour URI ?

    # coop_geo must be loaded BEFORE coop_local
    if "coop_geo" in settings.INSTALLED_APPS:
        location = models.ForeignKey(Location, null=True, blank=True, verbose_name=_(u'location'))
        area = models.ForeignKey(Area, null=True, blank=True, verbose_name=_(u'area'))    

    def __unicode__(self):
        return unicode(self.title)

    def get_absolute_url(self):
        return reverse('exchange_detail', args=[self.uuid])

    #TODO assign the record to the person editing it (form public) and provide an A-C choice in admin

    @property
    def uri_id(self):
        return self.uuid
    uri_fragment = 'exchange'

    class Meta:
        abstract = True
        verbose_name = _(u'Exchange')
        verbose_name_plural = _(u'Exchanges')


class BaseTransaction(models.Model):
    origin = models.ForeignKey('coop_local.Exchange', related_name='origin', verbose_name=_(u'origin'))
    destination = models.ForeignKey('coop_local.Exchange', related_name='destination', verbose_name=_(u'destination'))
    origin_org = models.ForeignKey('coop_local.Organization', related_name='contrats_vente', verbose_name=_(u'vendor'), blank=True, null=True)
    destination_org = models.ForeignKey('coop_local.Organization', related_name='contrats_achat', verbose_name=_(u'buyer'), blank=True, null=True)
    title = models.CharField(_('title'), blank=True, max_length=250)
    description = models.TextField(_(u'description'), blank=True)
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)
    uuid = exfields.UUIDField()  # nécessaire pour URI ?

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        verbose_name = _(u'Transaction')
        verbose_name_plural = _(u'Transactions')


# MODALITIES = Choices(
#     ('GIFT',    1,  _(u'Gift')),
#     ('TROC',    2,  _(u'Free exchange')),
#     ('CURR',    3,  _(u'Monetary exchange')),
# )
# UNITS = Choices(
#     ('EURO',    1,  _(u'€')),
#     ('SELH',    2,  _(u'Hours')),
#     ('PEZ',     3,  _(u'PEZ')),    
# )


# class BasePaymentModality(models.Model):
#     exchange = models.ForeignKey('coop_local.Exchange', verbose_name=_(u'exchange'), related_name='modalities')
#     modality = models.PositiveSmallIntegerField(_(u'exchange type'), blank=True,
#                                                 choices=MODALITIES.CHOICES,
#                                                 default=MODALITIES.CURR)
#     amount = models.DecimalField(_(u'amount'), max_digits=12, decimal_places=2, default=Decimal(0.00), blank=True)
#     unit = models.PositiveSmallIntegerField(_(u'unit'), blank=True, null=True, choices=UNITS.CHOICES)

#     def __unicode__(self):
#         if(self.modality in [1, 2]):
#             return unicode(MODALITIES.CHOICES_DICT[self.modality])
#         elif(self.modality == 3 and self.amount > 0 and not self.unit == None):
#             return unicode("%s %s" % (self.amount, unicode(UNITS.CHOICES_DICT[self.unit])))
#         elif(self.modality == 3):
#             return unicode(_(u'Price unknown'))

#     def save(self, *args, **kwargs):
#         if not self.modality == 3:
#             self.amount = Decimal(0.00)
#             self.unit = None
#         super(BasePaymentModality, self).save(*args, **kwargs) 

#     class Meta:
#         abstract = True
#         verbose_name = _(u'Payment modality')
#         verbose_name_plural = _(u'Payment modalities')




