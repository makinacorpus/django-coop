# -*- coding: utf-8 -*-


from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models.loading import get_model
from django.contrib.gis.db import models as gismodels
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget

from chosen import widgets as chosenwidgets
from extended_choices import Choices
import floppyforms as forms
import models

from ionyweb.forms import ModuloModelForm
from coop_local.models import Organization, LegalStatus, EvaluationAnswer
from coop.org.admin import OrganizationAdminForm, RelationInline
from coop.base_models import ActivityNomenclature, TransverseTheme, OrganizationCategory
from coop_local.models import Relation, Location, Document, Offer, Area
from coop.base_models import Located
from coop_geo.widgets import LocationPointWidget, ChooseLocationWidget, LocationPointWidgetInline
from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput, YearWidget
from .models import PageApp_Members




class PageApp_MembersForm(ModuloModelForm):

    class Meta:
        model = PageApp_Members

class PageApp_MembersSearchForm(ModuloModelForm):

    type = forms.CharField(required=False, label=_('Type'))
    
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    location = forms.CharField(required=False, label=_('Location'))
    location_id = forms.IntegerField(required=False)
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    statut = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    statut2 = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    
    category = forms.ModelChoiceField(queryset=OrganizationCategory.objects.all().order_by('label'),required=False, label=_('Category'))
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    date_start = forms.DateField(required=False)
    
    class Meta:
        model = PageApp_Members
        

class PageApp_MembersSortForm(forms.Form):
   CRITERIA = (
       ("", _("---")),
       ("location", _("Location")),
       ("alpha", _("Alpha")),
       ("creation", _("Date of creation")), 
       #(4, _("Solidarity")), 
   )
   sort = forms.ChoiceField(choices=CRITERIA)

   
class PartialMemberForm(OrganizationAdminForm):
    
    class Meta:
        model = Organization
        exclude = ('members', 'secteur_fse', 'sites', 'relations', 'statut', )
        widgets = {'logo' : CustomClearableFileInput(),}
        
    def __init__(self, *args, **kwargs):
        super(PartialMemberForm, self).__init__(*args, **kwargs)
        self.fields['short_description'].widget.attrs['onkeypress'] = 'return textCounter(this, 100);'
        self.fields['short_description'].widget.attrs['rows'] = '3'
        self.fields['short_description'].widget.attrs['cols'] = '40'        

        self.fields['description'].widget.attrs['rows'] = '15'
        self.fields['description'].widget.attrs['cols'] = '40'    
        
        self.fields['active'].label = _('Show on public site')

        self.fields['birth'].widget = YearWidget(years=[y for y in range(1900,2050)])
        
        self.fields['category'].queryset = OrganizationCategory.objects.all().order_by('label')
        
        
        
        
class CustomOfferForm(forms.ModelForm):        
    class Meta:
        model = Offer

    def __init__(self, *args, **kwargs):
        super(CustomOfferForm, self).__init__(*args, **kwargs)
        self.fields['activity'] = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.order_by('path'))
        #self.fields['area'] = forms.ModelChoiceField(queryset=Area.objects.order_by('label'))

class CustomRelationForm(forms.ModelForm):        
    class Meta:
        model = Relation

    def __init__(self, *args, **kwargs):
        super(CustomRelationForm, self).__init__(*args, **kwargs)
        self.fields['target'] = forms.ModelChoiceField(queryset=Organization.objects.order_by('title'))
        self.fields['target'].label = _("Target structure")
        
        
class CustomLocatedForm(forms.ModelForm):
    label = forms.CharField(required=False, label=_('Label'), help_text=_('Location and building name'))
    address = forms.CharField(required=False, label=_('Address'))
    city = forms.CharField(required=False, label=_('City'))
    zipcode = forms.CharField(required=False, label=_('Zipcode'))
    #point = forms.gis.PointField(required=False, label=_('Point'), widget=forms.gis.BaseOsmWidget(attrs={'map_width': 300,'map_height': 300}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION, help_text=_('You may point manually the location of the location'))
    point = forms.gis.PointField(required=False, label=_('Point'), widget=LocationPointWidgetInline(attrs={'map_width': 300,'map_height': 300, 'result_height': 100}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION, help_text=_('You may point manually the location of the location'))
    
    #point = forms.gis.PointField(label=_('Point'), widget=LocationPointWidget, null=True,srid=settings.COOP_GEO_EPSG_PROJECTION)
    #point = forms.gis.PointField(label=_('Point'), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION)
    #point = forms.gis.PointField(required=False, label=_('Point'), widget=LocationPointWidget(attrs={'map_width': 300,'map_height': 300}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION)
    # LocationPointWidget does not seem to work in formset due to numbers in JS variables
    
    
    class Meta:
        model = Located

        fields = ('label', 'address', 'city', 'zipcode', 'point', 'opening', 'main_location')

        widgets = {
            #'point': ChooseLocationWidget(forms.gis.PointWidget(), forms.gis.BaseOsmWidget(attrs={'map_width': 300,'map_height': 300})),
            #'point': LocationPointWidget(attrs={'map_width': 300,'map_height': 300})
        }
        
        
    def __init__(self, *args, **kwargs):
        super(CustomLocatedForm, self).__init__(*args, **kwargs)
        
        try:
            location = self.instance.location
        except Location.DoesNotExist:
            location = None

        if location :
            self.fields['label'].initial = location.label
            self.fields['address'].initial = location.adr1
            self.fields['city'].initial = location.city
            self.fields['zipcode'].initial = location.zipcode
            self.fields['point'].initial = location.point
            
            self.fields['opening'].help_text = _('Presentation sample: Monday 9h-12h  14h-17h / Tuesday  9h-12h  14h-17h / Wed.  14h-17h')
        
    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data
        
    def save(self, commit=True):
        located = super(CustomLocatedForm, self).save(commit=False)
        
        if self.cleaned_data:
            location = self.instance.location
            if location == None:
                location = Location()

            location.label = self.cleaned_data['label']
            location.adr1 = self.cleaned_data['address']
            location.zipcode = self.cleaned_data['zipcode']
            location.city = self.cleaned_data['city']
            location.point = self.cleaned_data['point']
            if commit:
                location.save()
      
            located.location = location            
      
        if commit:
            located.save()
        return located

        
        
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
        

class EvaluationAnswerForm(ModelForm):
    class Meta:
        model = EvaluationAnswer

    def __init__(self, *args, **kwargs):
        super(EvaluationAnswerForm, self).__init__(*args, **kwargs)
        self.fields['experience'].widget.attrs['rows'] = '3'
        self.fields['experience'].widget.attrs['cols'] = '60'        
        
                