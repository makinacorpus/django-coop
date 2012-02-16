# -*- coding:utf-8 -*-
from django.contrib import admin
from coop_local.models import Person,PersonCategory, Role,Engagement, \
    OrganizationCategory, Organization, SeeAlsoLink, SameAsLink, Relation,\
    Exchange, PaymentModality, Contact
from coop.admin import LocatedInline, AreaInline, BaseEngagementInline, \
    BaseOrganizationAdmin, BasePersonAdmin, \
    BaseRelationInline, BaseOrgInline, BaseExchangeInline, \
    BaseExchangeAdmin, BasePaymentInline

from coop.utils.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

admin.site.register(Role)
admin.site.register(PersonCategory)
admin.site.register(OrganizationCategory)

#from genericadmin.admin import GenericAdminModelAdmin,GenericTabularInline
from django.contrib.contenttypes.generic import GenericTabularInline

class ContactInline(GenericTabularInline):
    model = Contact
    extra=1

class SeeAlsoInline(GenericTabularInline):
    model = SeeAlsoLink
    extra=1
    
class SameAsInline(GenericTabularInline):
    model = SameAsLink
    extra=1    

class PaymentInline(BasePaymentInline):
    model = PaymentModality
    extra = 0

class ExchangeInline(BaseExchangeInline):
    model = Exchange
    extra=1    

class EngagementInline(BaseEngagementInline,InlineAutocompleteAdmin):
    model = Engagement

class OrgInline(BaseOrgInline,InlineAutocompleteAdmin):
    model = Engagement


class RelationInline(BaseRelationInline,InlineAutocompleteAdmin):
    model = Relation

# class OrganizationAdminForm(BaseOrganizationAdminForm):
#     class Meta:
#         model = Organization
# cool pas besoin de ça

class OrganizationAdmin(BaseOrganizationAdmin,FkAutocompleteAdmin):
    #form = OrganizationAdminForm
    inlines = [
        ContactInline,
        EngagementInline,
        ExchangeInline,
        LocatedInline,
        AreaInline,
        SeeAlsoInline,
        RelationInline
        ]
    fieldsets = BaseOrganizationAdmin.fieldsets + (
    ('CREDIS', {'fields': (('statut','secteur_fse'),('siret','naf'))}),
    )    
    
admin.site.register(Organization, OrganizationAdmin)


class PersonAdmin(BasePersonAdmin):
    inlines = [
            ContactInline,
            OrgInline,
            # SeeAlsoInline,
        ]

admin.site.register(Person, PersonAdmin)


class ExchangeAdmin(BaseExchangeAdmin):
    fieldsets = ((None, {
            'fields' : ('etype',('permanent','expiration',),'title','description',
                        #'tags',
                        'org'
                       )
            }),)
    inlines = [
            PaymentInline,
            LocatedInline, 
        ]

admin.site.register(Exchange, ExchangeAdmin)

#admin.site.register(PaymentModality)


from coop_cms.admin import ArticleAdmin as CmsArticleAdmin

class ArticleAdmin(CmsArticleAdmin):
    fieldsets = CmsArticleAdmin.fieldsets + (
        ('Misc', {'fields': ('author',)}),
    )

from coop_cms.settings import get_article_class
admin.site.unregister(get_article_class())
admin.site.register(get_article_class(), ArticleAdmin)




