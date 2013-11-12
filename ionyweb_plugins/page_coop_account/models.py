# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext

from extended_choices import Choices

from registration.models import RegistrationProfile


from ionyweb.page.models import AbstractPageApp
from coop_local.models import Organization, ActivityNomenclature, Area, TransverseTheme



class PageApp_CoopAccount(AbstractPageApp):
    
    # Define your fields here

    def __unicode__(self):
        return u'CoopAccount #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopAccount")



class AccountRegistrationView(FormView):
    
    #template_name = 'authentication/registration_form.html'
    #form_class = RegistrationForm
    #url = lazy_reverse('core:core-welcome')

    extra_context = {
        
    }
          
    def form_valid(self, form):
        AccountRegistrationView.register_user(self.request, **form.cleaned_data)
       
        return super(AccountRegistrationView, self).form_valid(self, form)
            
    def get_context_data(self, **kwargs):
        context = super(AccountRegistrationView, self).get_context_data(**kwargs)
        
        context.update(self.extra_context)
        return context
    
    @classmethod
    def register_user(cls, request, **kwargs):
        '''
        Given an email address and password, create a new
        user account, which will initially be inactive.
        '''
        
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']       
        user = cls.create_unique_user(username, email, password)
        
        cls.user_registered(user, request)
        
        return user
    
    @classmethod        
    def user_registered(cls, user, request):
        '''
        Handles successful user registrations.
        
        Creates a registration success messages and sends 
        a registration success email to the user.
        '''
        
        activation_key = RegistrationProfile.objects.get(user=user).activation_key
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        expiration_days = settings.ACCOUNT_ACTIVATION_DAYS
                   
        plaintext = get_template('page_coop_account/activation_email.txt')

        d = Context({ 'activation_key': activation_key , 'site': site, 'expiration_days': expiration_days })

        text_content = plaintext.render(d)

        title_template = get_template('page_coop_account/activation_email_subject.txt')
        title = title_template.render(Context({}))
        
        sender = settings.MAIN_EMAIL
        msg = EmailMultiAlternatives(title, text_content, sender, [user.email])
        
        try:
            res = msg.send()
            render_template = 'page_coop_account/activation_complete.html'
        except:   
            render_template = 'page_coop_account/activate.html'
                   
        
    @classmethod
    def create_unique_user(cls, username, email, password):
        '''
        Creates a unique user
        '''

        create_inactive_user = RegistrationProfile.objects.create_inactive_user

        if Site._meta.installed: #@UndefinedVariable
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        try:
            user = create_inactive_user(username, email, password, site, send_email=False)

            return user
        except IntegrityError:
            pass
            #return cls.create_unique_user(username, email, password)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            # Redirect registered users
            return HttpResponseRedirect(reverse('submissions:submissions-submission-list'))
        else:
            return super(AccountRegistrationView, self).dispatch(request, *args, **kwargs)

