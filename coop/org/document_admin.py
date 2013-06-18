from coop.utils.autocomplete_admin import GenericInlineAutocompleteAdmin
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model


class DocumentInline(GenericInlineAutocompleteAdmin):

    model = get_model('coop_local', 'Document')
    verbose_name = _(u'document')
    verbose_name_plural = _(u'documents')
    extra = 1
