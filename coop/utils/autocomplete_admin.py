from django.contrib import admin
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.admin.templatetags.admin_static import static
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.html import escape, escapejs
from django.forms.widgets import Select
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.safestring import mark_safe

from selectable.base import ModelLookup
from selectable.forms import AutoCompleteSelectWidget, AutoComboboxSelectWidget
from selectable.registry import registry, LookupAlreadyRegistered

import operator


class EditMixin(object):

    def __init__(self, rel, admin_site, *args, **kwargs):
        self.rel = rel
        self.admin_site = admin_site
        self.can_change_related = kwargs.pop('can_change_related', False)
        return super(EditMixin, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        markup = super(EditMixin, self).render(name, value, attrs)
        if self.can_change_related:
            rel_to = self.rel.to
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = reverse('admin:%s_%s_change' % info, args=[0], current_app=self.admin_site.name)
            markup += u'&nbsp;<a href="%s" class="changelink" id="change_id_%s" onclick="return showChangePopup(this);">' % (related_url, name)
            markup += u'<img src="%s"></a>' % static('admin/img/icon_changelink.gif')
        return mark_safe(markup)


class SelectEditWidget(EditMixin, Select):
    pass


class AutoCompleteSelectEditWidget(EditMixin, AutoCompleteSelectWidget):
    pass


class AutoComboboxSelectEditWidget(EditMixin, AutoComboboxSelectWidget):
    pass


class SelectableAdminMixin(object):

    related_search_fields = {}
    related_combobox = ()

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, models.ForeignKey):
            request = kwargs.get("request")
            related_modeladmin = self.admin_site._registry.get(db_field.rel.to)
            can_change_related = bool(related_modeladmin and
                        related_modeladmin.has_add_permission(request))
        if (isinstance(db_field, models.ForeignKey) and
            db_field.name in self.related_search_fields):
            class_name = self.__class__.__name__.lower()
            model_name = db_field.name
            name = u'%s-%s' % (class_name, model_name)
            class Lookup(ModelLookup):
                model = db_field.rel.to
                search_fields = ['%s__icontains' % f for f in self.related_search_fields[db_field.name]]
                def _name(cls):
                    return name
                name = classmethod(_name)
                def get_query(self, request, term):
                    qs = self.get_queryset()
                    if term:
                        for bit in term.split():
                            or_queries = [models.Q(**{field_name: smart_str(bit)})
                                    for field_name in self.search_fields]
                            qs = qs.filter(reduce(operator.or_, or_queries))
                    return qs
            try:
                registry.register(Lookup)
            except LookupAlreadyRegistered:
                pass
            if db_field.name in self.related_combobox:
                kwargs['widget'] = AutoComboboxSelectEditWidget(db_field.rel,
                    self.admin_site, Lookup, can_change_related=can_change_related)
            else:
                kwargs['widget'] = AutoCompleteSelectEditWidget(db_field.rel,
                    self.admin_site, Lookup, can_change_related=can_change_related)
        elif isinstance(db_field, models.ForeignKey):
            kwargs['widget'] = SelectEditWidget(db_field.rel, self.admin_site,
                can_change_related=can_change_related)
        return super(SelectableAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)

    def response_change(self, request, obj):
        if "_popup" in request.POST:
            pk_value = obj._get_pk_val()
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escapejs(obj)))
        return super(SelectableAdminMixin, self).response_change(request, obj)


class InlineAutocompleteAdmin(SelectableAdminMixin, admin.TabularInline):
    pass


class FkAutocompleteAdmin(SelectableAdminMixin, admin.ModelAdmin):
    pass


class NoLookupsFkAutocompleteAdmin(SelectableAdminMixin, admin.ModelAdmin):
    pass


class GenericInlineAutocompleteAdmin(SelectableAdminMixin, GenericTabularInline):
    pass


def register(model, model_admin=FkAutocompleteAdmin):
    admin.site.register(model, model_admin)
