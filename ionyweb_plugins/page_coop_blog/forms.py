# -*- coding: utf-8 -*-


from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from datetime import datetime
import floppyforms as forms
from extended_choices import Choices

from ionyweb.forms import ModuloModelForm
from ionyweb.widgets import DatePicker
from .models import CoopEntry, Category, PageApp_CoopBlog
from ionyweb.widgets import DateTimePicker, SlugWidget, DatePicker, TinyMCELargeTable
from coop.base_models import ActivityNomenclature, TransverseTheme, Document 
from coop_local.widgets import CustomCheckboxSelectMultiple

class PageApp_BlogForm(ModuloModelForm):

    class Meta:
        model = PageApp_CoopBlog


class CategoryForm(ModuloModelForm):

    class Meta:
        model = Category
        exclude = ('blog', )
        widgets = {
            'slug': SlugWidget('name'),
        }


class EntryForm(ModuloModelForm):

    class Meta:
        model = CoopEntry
        exclude = ('blog','category','slug','docs','author', )
        widgets = {
            'publication_date': DateTimePicker,
            'body': TinyMCELargeTable(attrs={'cols': 80, 'rows': 15,}),
            'slug': SlugWidget('title'),
        }
        
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['resume'].label = _("Resume")


EDATE = Choices(
    ('',    '',  _(u'-----')),
    ('3days',    '3',  _(u'Since 3 days')),
    ('week',   '7',  _(u'Since a week')),
    ('month',   '30',  _(u'Since a month')),
)        

class PageApp_CoopBlogForm(ModuloModelForm):
    
    class Meta:
        model = PageApp_CoopBlog


class PageApp_CoopBlogSearchForm(ModuloModelForm):

    date = forms.ChoiceField(required=False, choices=EDATE)
    
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    organization = forms.CharField(required=False, label=_('Organization'))
    
    tags = forms.CharField(required=False, label=_('Keywords'))
    
    class Meta:
        model = PageApp_CoopBlog
        exclude = ('title', )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    def clean_attachment(self):
        content = self.cleaned_data['attachment']
        if content.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(_('Please keep filesize under %(max_size)s. Current filesize %(current_size)s') % {'max_size':filesizeformat(settings.MAX_UPLOAD_SIZE), 'current_size':filesizeformat(content.size)})
        return content          