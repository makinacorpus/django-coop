# -*- coding: utf-8 -*-
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms
from extended_choices import Choices

from registration.forms import RegistrationForm

from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopAccount
from coop_local.models import PersonPreferences, ActivityNomenclature, Organization, Area
from coop_local.widgets import CustomCheckboxSelectMultiple



class PageApp_CoopAccountForm(ModuloModelForm):
    
    class Meta:
        model = PageApp_CoopAccount


class PageApp_CoopAccountPreferencesForm(ModuloModelForm):

    def __init__(self, *args, **kwargs):
        super(PageApp_CoopAccountPreferencesForm, self).__init__(*args, **kwargs)
        self.fields['activities'] = forms.ModelMultipleChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'), required=False)
        self.fields['organizations'] = forms.ModelMultipleChoiceField(queryset=Organization.objects.order_by('title'), required=False)
        self.fields['locations'] = forms.ModelMultipleChoiceField(queryset=Area.objects.order_by('label'), required=False)
        
    class Meta:
        model = PersonPreferences

class PageApp_CoopRegistrationForm(RegistrationForm):

    firstname = forms.CharField(label=_('firstname'),max_length=100)
    lastname = forms.CharField(label=_('lastname'),max_length=100)


        
        