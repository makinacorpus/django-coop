# -*- coding: utf-8 -*-

from datetime import datetime
import floppyforms as forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from ionyweb.forms import ModuloModelForm
from ionyweb.widgets import DatePicker
from .models import CoopEntry, Category, PageApp_Coop_Blog

from ionyweb.widgets import DateTimePicker, SlugWidget, DatePicker, TinyMCELargeTable
from coop.base_models import ActivityNomenclature, TransverseTheme

class PageApp_BlogForm(ModuloModelForm):

    class Meta:
        model = PageApp_Coop_Blog


class CategoryForm(ModuloModelForm):

    class Meta:
        model = Category
        exclude = ('blog', )
        widgets = {
            'slug': SlugWidget('name'),
        }

class EntryForm(ModuloModelForm):
    author = forms.ModelChoiceField(label=_('author'),
                                    queryset=User.objects.all(), 
                                    empty_label=None)

    #def __init__(self, authors_choices, categories_set, *args, **kwargs):
        #super(EntryForm, self).__init__(*args, **kwargs)
        #self.fields['category'].queryset = categories_set
        #self.fields['author'].choices = authors_choices
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        #self.fields['category'].queryset = categories_set
        #self.fields['author'].choices = authors_choices

    class Meta:
        model = CoopEntry
        exclude = ('blog', )
        widgets = {
            'publication_date': DateTimePicker,
            'body': TinyMCELargeTable(attrs={'cols': 80, 'rows': 15,}),
            'slug': SlugWidget('title'),
        }

class PageApp_CoopBlogForm(ModuloModelForm):

    date = forms.DateField(required=False)

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic3 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    organization = forms.CharField(required=False, label=_('Organization'))
    
    class Meta:
        model = PageApp_Coop_Blog
        