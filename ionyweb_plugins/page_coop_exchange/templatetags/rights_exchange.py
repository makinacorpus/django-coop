from django import template
from coop_local.models import Exchange, Person

register = template.Library()


def tag_rights_exchange(exchange, request):
    can_edit = False

    if request.user.is_superuser:
        can_edit = True
    else:
        if request.user.is_authenticated():
            try:
                pes_user = Person.objects.get(user=request.user)
            except Person.DoesNotExist:
                pes_user = None

            if pes_user :
                if exchange:
                    if exchange.person == pes_user:
                        can_edit = True
    return can_edit

register.filter('tag_rights_exchange', tag_rights_exchange)

