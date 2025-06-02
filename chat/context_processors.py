def current_user_id(request):
    return {
        'current_user_id': request.user.id if request.user.is_authenticated else None
    }
