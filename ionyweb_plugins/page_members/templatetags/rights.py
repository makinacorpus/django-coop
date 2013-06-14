from django import template
from coop_local.models import Engagement, Person

register = template.Library()


def tag_rights(member_id, request):
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
                if member_id:
                    try:
                        engagement = Engagement.objects.get(person_id=pes_user.pk, organization_id=member_id)
                    except Engagement.DoesNotExist:
                        engagement = None
                else:
                    try:
                        engagement = Engagement.objects.get(person_id=pes_user.pk)
                    except Engagement.DoesNotExist:
                        engagement = None

                if engagement and engagement.org_admin == True:
                    can_edit = True
            
    return can_edit

    
register.filter('tag_rights', tag_rights)

