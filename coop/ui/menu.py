"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'devcoop.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    This is a base Menu for django-coop admin site.

    You can :
    - override the whole thing using the ADMIN_TOOLS_MENU setting
    - just add your own custom menus by passing a list of dicts in coop_local/local_settings.py :

    ADMINTOOLS_CUSTOM_MENUS = [
            {'title': 'My Own Menu',
             'icon': 'icon-tint icon-white',  # a bootstrap icon, see http://twitter.github.com/bootstrap/base-css.html#images
             'children': [
                            ('First sub-menu', '/admin/coop_local/my_custom_model/'),
                            ('Second sub-menu', '/admin/coop_local/another_custom_model/'),
                        ]}
                ]

    """

    def init_with_context(self, context):
        super(CustomMenu, self).init_with_context(context)
        self.children = [
            #items.MenuItem(_(u'Dashboard'), reverse('admin:index')),
            #items.Bookmarks(u'Favoris'),

            #items.MenuItem(_(u'Navigation tree'), '/admin/coop_local/navtree/1/', icon='icon-list-alt icon-white'),

            #items.MenuItem(_(u'Articles'), '/admin/coop_local/article/', icon='icon-pencil icon-white'),

            items.MenuItem(_(u'CMS'), '#', icon='icon-cog icon-white',
                children=[

                    #items.MenuItem(_(u'Content'), '#', icon='icon-file', children=[
                        #items.MenuItem(_(u'Article categories'), '/admin/coop_cms/articlecategory/'),
                        #items.MenuItem(_(u'Documents'), '/admin/coop_cms/document/'),
                        #items.MenuItem(_(u'Images'), '/admin/coop_cms/image/'),
                        ## items.MenuItem(_(u'Newsletters'), '/admin/coop_local/newsletter/'),
                        ## items.MenuItem(_(u'MailingLists'), '/admin/coop_local/mailinglist/'),
                        #items.MenuItem(_(u'Comments'), '/admin/comments/comment/'),
                        #items.MenuItem(_(u'Forms'), '/admin/forms/form/'),
                        #items.MenuItem(_(u'Preferences'), '/admin/coop_local/siteprefs/'),

                        #]),

                    # RSS Sync menu gets inserted here if installed (see above)

                    items.MenuItem(_(u'Tags'), '#', icon='icon-tags', children=[
                        items.MenuItem(_(u'Tags'), '/admin/coop_local/tag/'),
                        #items.MenuItem(_('Tag categories'), '/admin/coop_tag/tagcategory/'),
                        items.MenuItem(_(u'Tag trees'), '/admin/coop_local/navtree/'),
                        ]),

                    items.MenuItem(_(u'Django'), '#', icon='icon-coop icon-django', children=[
                        items.MenuItem(_(u'Users'), '/admin/auth/user/'),
                        items.MenuItem(_(u'Sites'), '/admin/sites/site/'),
                        ]),
                ]
            ),


            # Agenda menu inserted here if coop.agenda installed

            items.MenuItem(_('Network'), '#', icon='icon-coop icon-group icon-white',
                children=[

                    items.MenuItem(_('Directory'), '#', icon='icon-home', children=[
                        items.MenuItem(_(u'Organizations'), '/admin/coop_local/organization/'),
                        items.MenuItem(_(u'Persons'), '/admin/coop_local/person/'),
                        items.MenuItem(_(u'Organization categories'), '/admin/coop_local/organizationcategory/'),
                        items.MenuItem(_(u'Person categories'), '/admin/coop_local/personcategory/'),
                        items.MenuItem(_(u'Roles'), '/admin/coop_local/role/'),
                        items.MenuItem(_(u'Activity nomenclature'), '/admin/coop_local/activitynomenclature/'),
                        items.MenuItem(_(u'Activity nomenclature AVISE'), '/admin/coop_local/activitynomenclatureavise/'),
                        items.MenuItem(_(u'Transverse Themes'), '/admin/coop_local/transversetheme/'),
                        ]),

                    items.MenuItem(_(u'Exchanges'), '#', icon='icon-random', children=[
                        items.MenuItem(_(u'Exchanges'), '/admin/coop_local/exchange/'),
                        items.MenuItem(_(u'Exchange methods'), '/admin/coop_local/exchangemethod/'),
                        ]),

                    items.MenuItem(_(u'Cartography'), '#', icon='icon-map-marker', children=[
                        items.MenuItem(_(u'Locations'), '/admin/coop_local/location/'),
                        items.MenuItem(_(u'Areas'), '/admin/coop_local/area/'),
                        items.MenuItem(_(u'Location categories'), '/admin/coop_geo/locationcategory/'),
                        # create my map !
                        ]),

                    items.MenuItem(_(u'RDF settings'), '#', icon='icon-coop icon-rdf', children=[
                        items.MenuItem(_(u'URI redirection'), '/admin/uriredirect/'),
                        # webid
                        ]),


                ]
            ),


        ]

        if 'coop_cms.apps.rss_sync' in settings.INSTALLED_APPS:
            self.children[0].children.insert(1,

                    items.MenuItem(_(u'RSS'), '#', icon='icon-coop icon-rss', children=[
                        items.MenuItem(_(u'RSS items'), '/admin/rss_sync/rssitem/'),
                        items.MenuItem(_(u'RSS sources'), '/admin/rss_sync/rsssource/'),
                        ])
                    )

        if 'coop.agenda' in settings.INSTALLED_APPS:
            self.children.insert(0,
                items.MenuItem(_(u'Agenda'), '#', icon='icon-calendar icon-white',
                    children=[
                        items.MenuItem(_(u'Events'), '/admin/coop_local/event/'),
                        items.MenuItem(_(u'Calendar'), '/admin/coop_local/calendar/'),
                        items.MenuItem(_(u'Event categories'), '/admin/coop_local/eventcategory/'),
                    ])
                )

        if 'coop.mailing' in settings.INSTALLED_APPS:
            if 'coop.agenda' in settings.INSTALLED_APPS:
                menu_nb = 1
            else:
                menu_nb = 0

            self.children[menu_nb].children[0].children.insert(3, 
                    items.MenuItem(_(u'Newsletters'), '/admin/coop_local/newsletter/'),)
            self.children[menu_nb].children[0].children.insert(4, 
                    items.MenuItem(_(u'MailingLists'), '/admin/coop_local/mailinglist/'),)


        if 'coop.project' in settings.INSTALLED_APPS:
            if 'coop.agenda' in settings.INSTALLED_APPS:
                menu_nb = 2
            else:
                menu_nb = 1

            self.children[menu_nb].children.insert(1,

                    items.MenuItem(_(u'Projects'), '#', icon='icon-book', children=[
                        items.MenuItem(_(u'Projects'), '/admin/coop_local/project/'),
                        items.MenuItem(_(u'Projects categories'), '/admin/coop_local/projectcategory/'),
                        ])
                    )

        is_superuser = context['request'].user.is_superuser

        if is_superuser:
            self.children.append(
                items.MenuItem(_('Thesaurus'), '#', icon='icon-coop icon-rdf icon-white', children=[
                    items.MenuItem(_('Location categories'), '/admin/coop_geo/locationcategory/'),
                    items.MenuItem(_('Person categories'), '/admin/coop_local/personcategory/'),
                    items.MenuItem(_('Customer targets'), '/admin/coop_local/clienttarget/'),
                    #items.MenuItem(_('Agreements IAE'), '/admin/coop_local/agreementiae/'),
                    #items.MenuItem(_('Guaranties'), '/admin/coop_local/guaranty/'),
                    items.MenuItem(_('Tags'), '/admin/coop_local/tag/'),
                    items.MenuItem(_('Activity nomenclature'), '/admin/coop_local/activitynomenclature/'),
                    items.MenuItem(_('Roles'), '/admin/coop_local/role/'),
                    #items.MenuItem(_('Legal statuses'), '/admin/coop_local/legalstatus/'),
                    items.MenuItem(_('Themes'), '/admin/coop_local/transversetheme/'),
                    items.MenuItem(_('Document types'), '/admin/coop_local/documenttype/'),
                    items.MenuItem(_('ESS categories'), '/admin/coop_local/organizationcategory/'),
                    #items.MenuItem(_('IAE categories'), '/admin/coop_local/categoryiae/'),
                ])
            )

        try:    
            idx = len(self.children)
            for menu in settings.ADMINTOOLS_CUSTOM_MENUS:
                self.children.insert(idx, items.MenuItem(
                    menu['title'], '#',
                    icon=menu['icon'],
                    children=[items.MenuItem(x[0], x[1]) for x in menu['children']]
                    ))
                idx += 1
        except AttributeError:
            pass        
