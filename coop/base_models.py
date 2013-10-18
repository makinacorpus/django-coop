# -*- coding:utf-8 -*-

from django.conf import settings
from coop.link.models import BaseLinkProperty, BaseLink
from coop.person.models import BasePerson, BasePersonCategory, BasePersonPreferences
from coop.exchange.models import BaseExchange, BaseProduct, BaseExchangeMethod
from coop.org.models import (BaseOrganizationCategory, BaseOrganization,
                             BaseRelation, BaseEngagement, BaseRole, BaseOrgRelationType,
                             BaseContact, BaseRoleCategory, BaseContactMedium,
                             BaseActivityNomenclature, BaseActivityNomenclatureAvise,
                             BaseTransverseTheme, BaseOffer, BaseClientTarget,
                             BaseDocumentType, BaseDocument, BaseGuaranty,
                             BaseLegalStatus, BaseReference)
from coop.prefs.models import BaseSitePrefs
from coop_geo.models import Location as BaseLocation
from coop_geo.models import Located as BaseLocated
from coop_geo.models import Area as BaseArea
from coop.rdf.models import DeletedURI as BaseDeletedURI


# ---- geo
class Location(BaseLocation):
    pass


class Located(BaseLocated):
    pass


class Area(BaseArea):
    pass


# ---- DeletedUri
class DeletedURI(BaseDeletedURI):
    pass


# ---- person


class LinkProperty(BaseLinkProperty):
    pass


class Link(BaseLink):
    pass


# ----- CMS

if 'coop.project' in settings.INSTALLED_APPS:
    from coop.article.models import CoopArticle, CoopNavTree

    class Article(CoopArticle):
        pass

    class NavTree(CoopNavTree):
        pass

if 'coop_tag' in settings.INSTALLED_APPS:
    from coop.tag.models import CoopTag, CoopTaggedItem

    # ----- Tag

    class Tag(CoopTag):
        pass

    class TaggedItem(CoopTaggedItem):
        pass


# ---- person


class PersonCategory(BasePersonCategory):
    pass

class PersonPreferences(BasePersonPreferences):
    pass

class Person(BasePerson):
    pass


# ----- org


class Reference(BaseReference):
    pass


class ContactMedium(BaseContactMedium):
    pass


class Contact(BaseContact):
    pass


class RoleCategory(BaseRoleCategory):
    pass


class Role(BaseRole):
    pass


class Relation(BaseRelation):
    pass


class Engagement(BaseEngagement):
    pass


class OrgRelationType(BaseOrgRelationType):
    pass


class OrganizationCategory(BaseOrganizationCategory):
    pass


class ClientTarget(BaseClientTarget):
    pass


class Offer(BaseOffer):
    pass


class DocumentType(BaseDocumentType):
    pass


class Document(BaseDocument):
    pass


class Guaranty(BaseGuaranty):
    pass


class LegalStatus(BaseLegalStatus):
    pass


class Organization(BaseOrganization):
    pass


class ActivityNomenclature(BaseActivityNomenclature):
    pass


class ActivityNomenclatureAvise(BaseActivityNomenclatureAvise):
    pass


class TransverseTheme(BaseTransverseTheme):
    pass


# ----- project

if 'coop.project' in settings.INSTALLED_APPS:
    from coop.project.models import BaseProjectSupport, BaseProject, BaseProjectCategory, BaseProjectMember

    class ProjectCategory(BaseProjectCategory):
        pass

    class ProjectSupport(BaseProjectSupport):
        pass

    class Project(BaseProject):
        pass

    class ProjectMember(BaseProjectMember):
        pass


# ------ exchange


class Exchange(BaseExchange):
    pass


class ExchangeMethod(BaseExchangeMethod):
    pass


class Product(BaseProduct):
    pass


# ----- mailing

if 'coop.mailing' in settings.INSTALLED_APPS:
    from coop.mailing.models import BaseSubscription, BaseMailingList, \
           BaseNewsletter, BaseNewsletterSending

    class MailingList(BaseMailingList):
        pass

    class Subscription(BaseSubscription):
        pass

    # class NewsletterItem(BaseNewsletterItem):
    #     pass

    class Newsletter(BaseNewsletter):
        pass

    class NewsletterSending(BaseNewsletterSending):
        pass


# ----- agenda

if 'coop.agenda' in settings.INSTALLED_APPS:
    from coop.agenda.models import BaseCalendar, BaseEvent, BaseEventCategory, \
            BaseOccurrence, BaseDated

    class Calendar(BaseCalendar):
        pass

    class Event(BaseEvent):
        pass

    class EventCategory(BaseEventCategory):
        pass

    class Occurrence(BaseOccurrence):
        pass

    class Dated(BaseDated):
        pass


# ------ global site preferences


class SitePrefs(BaseSitePrefs):
    pass
