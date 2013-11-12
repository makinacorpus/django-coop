from django import template
from coop_local.models import CoopEntry, Person

register = template.Library()


def tag_rights_entry(entry, request):
    can_edit = False

    if request.user.is_superuser:
        can_edit = True
    else:
        if entry:
            if entry.author == request.user:
                can_edit = True
    return can_edit

    
register.filter('tag_rights_entry', tag_rights_entry)

