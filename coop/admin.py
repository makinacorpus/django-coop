# -*- coding:utf-8 -*-
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.conf import settings
from tinymce.widgets import AdminTinyMCE
from django import forms
from sorl.thumbnail.admin import AdminImageMixin
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns
from coop.utils.autocomplete_admin import FkAutocompleteAdmin
from django.shortcuts import render_to_response
from django.template import RequestContext

from coop_local.models import Organization, Exchange, Occurrence
from ionyweb_plugins.page_coop_blog.models import CoopEntry

class ObjEnabledInline(InlineModelAdmin):
    # def __init__(self, *args, **kwargs):
    #     self.parent_object = kwargs['obj']
    #     del kwargs['obj']  # superclass will choke on this
    #     super(ObjEnabledInline, self).__init__(*args, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        # Hack! Hook parent obj just in time to use in formfield_for_manytomany
        self.parent_obj = obj
        return super(ObjEnabledInline, self).get_formset(
            request, obj, **kwargs)


class ObjEnabledAdmin(admin.ModelAdmin):  # TODO bring back the permissions code from original method ?

    def get_form(self, request, obj=None, **kwargs):
        # Hack! Hook parent obj just in time to use in formfield_for_manytomany
        self._obj = obj
        return super(ObjEnabledAdmin, self).get_form(
            request, obj, **kwargs)


if 'forms_builder.forms' in settings.INSTALLED_APPS:

    from forms_builder.forms.admin import FormAdmin
    from forms_builder.forms.models import Form

    class CoopFormAdmin(FormAdmin):
        change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
        fieldsets = [
            (_("Settings"), {"fields": ( "title",
                                    #("status", "login_required",),
                                    #("publish_date", "expiry_date",),
                                     "intro", "button_text", "response")}),
            (_("Email"), {"fields": ("send_email", "email_from", "email_copies",
                                     "email_subject", "email_message")}),
            ]
        list_display = ("title", "total_entries", "admin_links")
        list_display_links = ("title",)
        list_editable = []


# Obect validation view
def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
            (r'^objects_to_validate/$', admin.site.admin_view(objects_to_validate))
        )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls

def objects_to_validate(request):
    # list all objects that are waiting for a validation
    organizations_list = []
    exchanges_list = []
    occ_list = []
    projects_list = []
    entries_list = []

    # List all organizations
    organizations = Organization.objects.filter(is_project=False).exclude(status='V').order_by("-modified")
    for o in organizations:
        # automatic association of the user to this organization
        first_name = ''
        last_name = ''
        email = ''
        engagement = Engagement.objects.filter(organization=o)
        if engagement:
            if engagement.person:
                first_name = person.first_name
                last_name = person.last_name
                email = person.email
        url = "%sp/member_edit/%s" % (settings.COOP_MEMBER_ORGANIZATIONS_URL, o.pk)
        organizations_list.append({'title': o.title, 'first_name': first_name, 'last_name': last_name, 'email': email, 'url': url, 'status': o.get_status_display})
    
    # Exchanges
    exchanges = Exchange.objects.exclude(status='V').order_by("-modified")
    for e in exchanges:
        first_name = ''
        last_name = ''
        email = ''
        url = "%sp/exchange_edit/%s" % (settings.COOP_EXCHANGE_EXCHANGES_URL, e.pk)
        first_name = e.person.first_name
        last_name = e.person.last_name
        email = e.person.email
        exchanges_list.append({'title': e.title, 'first_name': first_name, 'last_name': last_name, 'email': email, 'url': url, 'status': e.get_status_display})
    
    # List all events
    occ = Occurrence.objects.exclude(event__status='V').order_by("start_time")
    for o in occ:
        first_name = ''
        last_name = ''
        email = ''
        url = "%sp/event_edit/%s" % (settings.COOP_AGENDA_URL, o.pk)
        if o.event.person:
            first_name = o.event.person.first_name
            last_name = o.event.person.last_name
            email = o.event.person.email
        occ_list.append({'title': o.title, 'first_name': first_name, 'last_name': last_name, 'email': email, 'url': url, 'status': o.event.get_status_display})

    
    # List all projects
    projects = Organization.objects.filter(is_project=True).exclude(status='V').order_by("-modified")
    for p in projects:
        # automatic association of the user to this organization
        first_name = ''
        last_name = ''
        email = ''
        engagement = Engagement.objects.filter(organization=p)
        if engagement:
            if engagement.person:
                first_name = person.first_name
                last_name = person.last_name
                email = person.email
        url = "%sp/project_edit/%s" % (settings.COOP_MEMBER_PROJECTS_URL, p.pk)
        projects_list.append({'title': p.title, 'first_name': first_name, 'last_name': last_name, 'email': email, 'url': url, 'status': p.get_status_display})

    # List all entries
    entries = CoopEntry.objects.exclude(status_moderation='V').order_by('-modification_date')
    for e in entries:
        first_name = ''
        last_name = ''
        email = ''
        url = "%sp/entry_edit/%s" % (settings.COOP_BLOG_URL, e.pk)
        first_name = e.author.first_name
        last_name = e.author.last_name
        email = e.author.email
        entries_list.append({'title': e.title, 'first_name': first_name, 'last_name': last_name, 'email': email, 'url': url, 'status': e.get_status_moderation_display})

    context = {'exchanges': exchanges_list, 'occ': occ_list, 'organizations': organizations_list, 'projects': projects_list, 'entries': entries_list}
    return render_to_response('admin/moderation.html', context, RequestContext(request))                       



#     def get_inline_instances(self, request, obj):
#         inline_instances = []
#         for inline_class in self.inlines:
#             if inline_class.__mro__.__contains__(ObjEnabledInline):
#                 inline = inline_class(self.model, self.admin_site, obj=obj)
#             else:
#                 inline = inline_class(self.model, self.admin_site)
#             inline_instances.append(inline)
#         return inline_instances



# from coop.org.models import BaseEngagement, BaseRelation
# from coop.person.models import BasePerson
# from coop.exchange.models import BaseExchange, BasePaymentModality, BaseTransaction, BaseProduct
# from django import forms
# from django.conf import settings

# # from django.contrib.admin.widgets import FilteredSelectMultiple
# from django.db.models.loading import get_model
# from django.utils.translation import ugettext_lazy as _
# from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin

# from coop_local.models import Contact, Person
# from coop_geo.models import Location
# from django.contrib.contenttypes.models import ContentType
# from django.db.models import Q

# from django.contrib.admin.widgets import AdminURLFieldWidget
# from django.db.models import URLField
# from django.utils.safestring import mark_safe

# from sorl.thumbnail.admin import AdminImageMixin

# from sorl.thumbnail import default
# ADMIN_THUMBS_SIZE = '60x60'


# class SimpleLinkWidget(forms.Widget):
#     def __init__(self, obj, attrs=None):
#         self.object = obj
#         super(SimpleLinkWidget, self).__init__(attrs)

#     def render(self, name, value, attrs=None):
#         if self.object.pk:
#             return mark_safe(
#                 u'<a target="_blank" href="../../../%s/%s/%s/">%s</a>' %\
#                       (
#                        self.object._meta.app_label,
#                        self.object._meta.object_name.lower(),
#                        self.object.pk,
#                        u'<b>Compléter la fiche détaillée</b>'
#                        )
#             )
#         else:
#             return mark_safe(u'')


# class M2MLinkWidget(forms.Widget):
#     def __init__(self, obj, fkey_name, attrs=None,):
#         self.object = obj
#         self.fkey = fkey_name
#         super(M2MLinkWidget, self).__init__(attrs)

#     def render(self, name, value, attrs=None):
#         if self.object.pk and self.fkey and getattr(self.object, self.fkey) != None:
#             return mark_safe(u'<a href="../../../%s/%s/%s/">%s</a>' % \
#                 (self.object._meta.app_label,
#                     getattr(self.object, self.fkey)._meta.object_name.lower(),
#                     getattr(self.object, self.fkey).pk,
#                     u' '.join((u'Fiche', unicode(self.fkey)))  # TODO how to get the translated app name ?
#                     )
#             )
#         else:
#             return mark_safe(u'')


# class ExchangeInlineLinkForm(forms.ModelForm):
#     class Meta:
#         model = BaseExchange
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(ExchangeInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = SimpleLinkWidget(self.instance)


# class ContactInlineLinkForm(forms.ModelForm):
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(ContactInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='person')


# class OrgInlineLinkForm(forms.ModelForm):
#     lien = forms.CharField(label='lien', required=False)

#     def __init__(self, *args, **kwargs):
#         super(OrgInlineLinkForm, self).__init__(*args, **kwargs)
#         self.fields['lien'].widget = M2MLinkWidget(self.instance, fkey_name='organization')


# # ---------- if coop-geo is installed --------------

# if "coop_geo" in settings.INSTALLED_APPS:
#     from coop_geo.admin import LocatedInline, AreaInline

# # ----------------------------------------------------








# # from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
# # from django.contrib.admin.util import get_model_from_relation
# # from django.db.models import Count


# # if "coop_tag" in settings.INSTALLED_APPS:

# #     #from taggit.managers import TaggableManager
# #     from taggit_autosuggest.managers import TaggableManager

# #     class TaggitFilterSpec(RelatedFilterSpec):
# #         """
# #         A FilterSpec that can be used to filter by taggit tags in the admin.
# #         To use, simply import this module (for example in `models.py`), and add the
# #         name of your :class:`taggit.managers.TaggableManager` field in the
# #         :attr:`list_filter` attribute of your :class:`django.contrib.ModelAdmin`
# #         class.
# #         """

# #         def __init__(self, f, request, params, model, model_admin,
# #                      field_path=None):
# #             super(RelatedFilterSpec, self).__init__(
# #                 f, request, params, model, model_admin, field_path=field_path)

# #             other_model = get_model_from_relation(f)
# #             if isinstance(f, (models.ManyToManyField,
# #                               models.related.RelatedObject)):
# #                 # no direct field on this model, get name from other model
# #                 self.lookup_title = other_model._meta.verbose_name
# #             else:
# #                 self.lookup_title = f.verbose_name  # use field name
# #             rel_name = other_model._meta.pk.name
# #             self.lookup_kwarg = '%s__%s__exact' % (self.field_path, rel_name)
# #             self.lookup_kwarg_isnull = '%s__isnull' % (self.field_path)
# #             self.lookup_val = request.GET.get(self.lookup_kwarg, None)
# #             self.lookup_val_isnull = request.GET.get(
# #                                           self.lookup_kwarg_isnull, None)
# #             # Get tags and their count
# #             # through_opts = f.through._meta
# #             # count_field = ("%s_%s_items" % (through_opts.app_label,
# #             #         through_opts.object_name)).lower()

# #             queryset = getattr(f.model, f.name).all()
# #             queryset = queryset.annotate(num_times=Count('ctagged_items'))
# #             queryset = queryset.order_by("-num_times")
# #             self.lookup_choices = [(t.pk, "%s (%s)" % (t.name, t.num_times))
# #                     for t in queryset[:20]]


# #     # HACK: we insert the filter at the beginning of the list to avoid the manager
# #     # to be picked as a RelatedFilterSpec
# #     FilterSpec.filter_specs.insert(0, (lambda f: isinstance(f, TaggableManager),
# #         TaggitFilterSpec))
