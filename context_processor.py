from mainapp.models import UserDetails
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist


def user_badges_Counts(request):
    allUsers_Count = UserDetails.objects.exclude(user_status="pending").count()
    pendingusers_Count = UserDetails.objects.filter(user_status="pending").count()

    context = {
        'allUsers_count': allUsers_Count,
        'pendingusers_count': pendingusers_Count
    }

    return context

def active_nav_item(request):
    current_url = resolve(request.path_info).url_name
    return {
        "active_nav_item": current_url
    }

def user_profile_details(request):
    user_id = request.session.get("user_id")  # Use get() to avoid KeyError

    if user_id is None:
        # Return empty context if user_id is not set
        return {
            'full_name': None,
            'image_url': None,
            'user_email': None,
        }

    try:
        dbUser = UserDetails.objects.get(user_id=user_id)
        context = {
            'full_name': dbUser.full_name,
            'image_url': dbUser.user_image,
            'user_email': dbUser.email,
        }
    except ObjectDoesNotExist:
        # Handle case where user does not exist
        context = {
            'full_name': None,
            'image_url': None,
            'user_email': None,
        }

    return context

