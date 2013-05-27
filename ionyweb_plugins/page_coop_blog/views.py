# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.views.generic.date_based import object_detail as django_object_detail
from django.utils.decorators import available_attrs
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from ionyweb.website.rendering import HTMLRendering
from ionyweb.website.rendering.medias import JSAdminMedia, RSSMedia
from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia

from models import PageApp_Coop_Blog, Category, CoopEntry
from forms import EntryForm, PageApp_CoopBlogForm

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


ACTIONS_MEDIAS = [
    JSAdminMedia('page_coop_blog_actions.js'),
]

MEDIAS = (
    CSSMedia('page_coop_blog.css'),
    )


def index_view(request, page_app):
    rdict = filter_data(request, page_app)
    return render_view('page_coop_blog/coopentry_archive.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           

    
def entries_queryset_view_to_app(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def __wrapped_view(request, obj, **kwargs):
        dict_args = dict(queryset=obj.online_entries.all())
        dict_args.update(kwargs)

        # '<link rel="alternate" type="application/rss+xml" title="RSS" href="%sp/feed/rss/" />'
        medias = [RSSMedia('%sp/feed/rss/' % obj.get_absolute_url()),]

        if request.is_admin:
            medias += ACTIONS_MEDIAS
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content), medias)
        else:
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content),
                                 medias)
    return __wrapped_view


def categories_queryset_view_to_app(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def __wrapped_view(request, obj, **kwargs):
        dict_args = dict(queryset=obj.online_categories.all())
        dict_args.update(kwargs)
        medias = [
            RSSMedia('%sp/feed/rss/%s/' % (obj.get_absolute_url(),
                                           kwargs['slug'])),
            ]
        if request.is_admin:
            medias += ACTIONS_MEDIAS
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content),
                                 medias)
        else:
            return HTMLRendering(mark_safe(view_func(request, **dict_args).content),
                             medias)
    return __wrapped_view


    
def filter_data(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())

    entries = CoopEntry.objects.all()
    more_criteria = False
    
    if request.method == 'POST': # If the form has been submitted        
        form = PageApp_CoopBlogForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                entries = entries.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['organization']:
                entries = entries.filter(Q(organization__in=form.cleaned_data['organization']))

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2'] or form.cleaned_data['thematic3']:
                entries = entries.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']) | Q(transverse_themes=form.cleaned_data['thematic3']))
            
            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                entries = entries.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
                
                
            #TODO : date
            
    else:
        form = PageApp_CoopBlogForm() # An empty form
        more_criteria = False
    
    
    rdict = {'entries': entries, 'base_url': base_url, 'form': form}
    
    return rdict

    
def detail_view(request, page_app, pk):
    e = get_object_or_404(CoopEntry, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': e, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_blog/entry_detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))
    
    
def add_view(request, page_app):
    if request.user.is_authenticated():
        base_url = u'%sp/entry_add' % (page_app.get_absolute_url())
        center_map = settings.COOP_MAP_DEFAULT_CENTER

        if request.method == 'POST': # If the form has been submitted        
            entry = CoopEntry()
            
            form = EntryForm(request.POST, instance = entry)
            
            if form.is_valid():

                entry.blog_id = 1
                entry = form.save()
                
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url}
                return render_view('page_coop_blog/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = EntryForm() # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'center': center_map}
        return render_view('page_coop_blog/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_blog/forbidden.html')


                       