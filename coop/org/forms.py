# -*- coding:utf-8 -*-
from django import forms
from django.conf import settings
import floppyforms
import re
from coop_local.models import Organization, OrganizationCategory
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

if 'coop_cms' in settings.INSTALLED_APPS:
    from djaloha.widgets import AlohaInput
    djaloha_widget_options = {'text_color_plugin': False}
else:
    from django.forms import TextInput as AlohaInput
    djaloha_widget_options = {}

class OrganizationForm(floppyforms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.org = kwargs.get('instance', None)
        #self.set_logo_size()

    class Meta:
        model = Organization
        fields = ('title', 'description', 'logo')
        widgets = {
            'title': AlohaInput(**djaloha_widget_options),
            'description': AlohaInput(**djaloha_widget_options),
        }

    # def set_logo_size(self, logo_size=None):
    #     thumbnail_src = self.logo_thumbnail(logo_size)
    #     update_url = reverse('coop_cms_update_logo', args=[self.article.id])
    #     self.fields['logo'].widget = ImageEdit(update_url, thumbnail_src.url if thumbnail_src else '')

    def logo_thumbnail(self, logo_size=None):
        if self.org:
            return self.org.logo_thumbnail(True, logo_size=logo_size)

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if title[-4:].lower() == '<br>':
            title = title[:-4]
        if not title:
            raise ValidationError(_(u"Title can not be empty"))
        if re.search(u'<(.*)>', title):
            raise ValidationError(_(u'HTML content is not allowed in the title'))
        return title


class OrganizationCategoryForm(floppyforms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrganizationCategoryForm, self).__init__(*args, **kwargs)
        self.org_category = kwargs.get('instance', None)

    class Meta:
        model = OrganizationCategory
        fields = ('label', 'description')
        widgets = {
            'label': AlohaInput(**djaloha_widget_options),
            'description': AlohaInput(**djaloha_widget_options),
        }

    def clean_label(self):
        label = self.cleaned_data['label'].strip()
        if label[-4:].lower() == '<br>':
            label = label[:-4]
        if not label:
            raise ValidationError(_(u"Label can not be empty"))
        if re.search(u'<(.*)>', label):
            raise ValidationError(_(u'HTML content is not allowed in the label'))
        return label


