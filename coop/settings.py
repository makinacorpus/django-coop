# -*- coding:utf-8 -*-

BASE_COOP_LOCAL_MODELS = [
    ('coop_geo', [
        u'Location', 
        u'Area',
    ]),
    ('coop_tag', [
        u'Tag',
        u'TaggedItem',
    ]),
    ('coop.agenda', [
        u'Calendar',
        u'Dated',
        u'Event',
        u'EventCategory',
        u'Occurrence',
    ]),
    ('coop.person', [
        u'Person',
        u'PersonCategory',
    ]),
    ('coop.org', [
        u'ContactMedium',
        u'Contact',
        u'Engagement',
        u'Role',
        u'RoleCategory',
        u'OrgRelationType',
        u'Relation',
        u'OrganizationCategory',
        u'Organization',
        u'ActivityNomenclature',
        u'ActivityNomenclatureAvise',
        u'TransverseTheme',
   ]),
    ('coop.project', [
        u'ProjectCategory',
        u'ProjectSupport',
        u'ProjectMember',
        u'Project',
    ]),
    ('coop.exchange', [
        u'ExchangeMethod',
        u'Product',
        u'Exchange',
    ]),
    ('coop.mailing', [
        u'MailingList',
        u'Subscription',
        # u'NewsletterItem',
        u'Newsletter',
        u'NewsletterSending',
    ]),
    ('coop.prefs', [
        u'SitePrefs',
    ]),
]
