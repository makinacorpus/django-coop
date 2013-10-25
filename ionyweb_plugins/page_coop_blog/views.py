# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.views.generic.date_based import object_detail as django_object_detail
from django.utils.decorators import available_attrs
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.simplejson import dumps
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from .forms import DocumentForm
from datetime import datetime, timedelta

from ionyweb.website.rendering import HTMLRendering
from ionyweb.website.rendering.medias import JSAdminMedia, RSSMedia
from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia

from models import PageApp_CoopBlog, Category, CoopEntry
from forms import EntryForm, PageApp_CoopBlogSearchForm
from coop_local.models import Document
from coop.base_models import Tag


ACTIONS_MEDIAS = [
    #JSAdminMedia('page_coop_blog_actions.js'),
]

MEDIAS = (
    CSSMedia('page_coop_blog.css'),
    JSAdminMedia('page_coop_blog_actions.js'),
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

    # Display entries that have a group associated (those one are privates)
    # only for users associated to this group
    if request.user.is_authenticated():
        entries = CoopEntry.objects.filter(Q(status=1, blog=page_app, group_private__isnull=True)| \
                                           Q(status=1, blog=page_app, group_private__in=request.user.groups.all)).order_by('-modification_date')
    else:
        entries = CoopEntry.objects.filter(Q(status=1, blog=page_app, group_private__isnull=True)).order_by('-modification_date')
        
    more_criteria = False
    
    if request.method == 'GET': # If the form has been submitted        
        form = PageApp_CoopBlogSearchForm(request.GET)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                entries = entries.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']) | Q(tagged_items__tag__name__in=[form.cleaned_data['free_search']]))
            
            if form.cleaned_data['thematic']:
                entries = entries.filter(Q(transverse_themes=form.cleaned_data['thematic']))
            
            if form.cleaned_data['activity']:
                activity = form.cleaned_data['activity']                    
                tab_keep = get_list_entrie_to_keep(entries, activity)
                entries = entries.filter(pk__in=tab_keep)
                
            if form.cleaned_data['date'] != '' :
                entries = entries.filter(Q(publication_date__gte=datetime.date(datetime.today() - timedelta(days = int(form.cleaned_data['date'])))))
            
    else:
        form = PageApp_CoopBlogSearchForm() # An empty form
        more_criteria = False

    paginator = Paginator(entries, 10)
    page = request.GET.get('page')
    try:
        entries_page = paginator.page(page)
    except PageNotAnInteger:
        entries_page = paginator.page(1)
    except EmptyPage:
        entries_page = paginator.page(paginator.num_pages)
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']    

    # Get entries title and tags for free search autocomplete
    tab_available_data = [{'label':e.title, 'value':e.pk} for e in CoopEntry.objects.filter(Q(status=1, blog=page_app, group_private__isnull=True)).order_by("title")]
    tab_available_data += [{'label':t.name, 'value':t.pk} for t in Tag.objects.all().order_by('name')]
    available_data = dumps(tab_available_data)        
        
    rdict = {'entries': entries_page, 'base_url': base_url, 'form': form, 'media_path': settings.MEDIA_URL, 'available_data': available_data}
    
    return rdict


def get_list_entrie_to_keep(entries, activity):    
    tab_keep = []
    for e in entries:
        if e.activity:
            parent = get_parent_activity_leve_0(e.activity)
            if parent == activity.label:
                tab_keep.append(e.pk)
    return tab_keep

def get_parent_activity_leve_0(activity):
    if activity.parent:
        return get_parent_activity_leve_0(activity.parent)
    else:
        return activity.label
        
        
def detail_view(request, page_app, pk):
    e = get_object_or_404(CoopEntry, pk=pk)

    # check if this article is accessible for this user
    viewable = False
    if e.group_private.exists() and not request.user.is_superuser:
        for gp in e.group_private.all():
            if gp in request.user.groups.all():
                viewable = True
        if viewable == False:
            return
    
    base_url = u'%sp/' % (page_app.get_absolute_url())
    imgs = e.document_set.filter(type__name='Galerie')
    docs = e.document_set.exclude(type__name='Galerie')
    
    more_articles = CoopEntry.objects.filter(author=e.author)

    print_css = 0
    if request.method == 'GET' and 'mode' in request.GET:
        if request.GET['mode'] == 'print':
            print_css = 1    
            
    rdict = {'object': page_app, 'e': e, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'imgs': imgs, 'docs': docs, 'more_articles': more_articles, "print_css": print_css}
    return render_view('page_coop_blog/entry_detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))
    
    
def add_view(request, page_app, entry_id=None):
    if request.user.is_authenticated():
        DocFormSet = generic_inlineformset_factory(Document, form=DocumentForm, extra=1)
        
        if entry_id:
            # update
            mode = 'update'
            entry = get_object_or_404(CoopEntry, pk=entry_id)
            base_url = u'%sp/entry_edit/%s' % (page_app.get_absolute_url(),entry_id)
            delete_url = u'%sp/entry_delete/%s' % (page_app.get_absolute_url(),entry_id)
            #if entry.owner != request.user and not Right.objects.has_right(request.user, entry, WRITE):
                #raise Http404
        else :
            # new
            mode = 'add'
            base_url = u'%sp/entry_add' % (page_app.get_absolute_url())
            delete_url = ''
            entry = CoopEntry()
        
        if request.method == 'POST': # If the form has been submitted        
            form = EntryForm(request.POST, request.FILES, instance = entry)
            docFormset = DocFormSet(request.POST, request.FILES, prefix='doc', instance=entry)
            
            if form.is_valid() and docFormset.is_valid():
            
                if not entry_id:
                    entry.slug = slugify(entry.title)
                
                
                entry.blog = page_app # default blog
                entry.author = request.user
                entry = form.save()
                docFormset.save()
                
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'mode': mode, 'entry_id' : entry.pk}
                return render_view('page_coop_blog/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = EntryForm(instance=entry)
            docFormset = DocFormSet(prefix='doc', instance=entry)
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'delete_url': delete_url, 'form': form, 'doc_form': docFormset, 'mode': mode}
        return render_view('page_coop_blog/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_blog/forbidden.html')


def delete_view(request, page_app, entry_id):
    # check rights    
    can_edit = False
    if CoopEntry.objects.get(pk=entry_id).author == request.user or request.user.is_superuser:
        can_edit = True
    
    if can_edit :
        u = CoopEntry.objects.get(pk=entry_id).delete()
        base_url = u'%s' % (page_app.get_absolute_url())
        rdict = {'base_url': base_url}
        return render_view('page_coop_blog/delete_success.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_blog/forbidden.html')     
       