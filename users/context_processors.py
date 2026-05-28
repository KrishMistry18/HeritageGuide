def firebase_user(request):
    """
    Exposes the Firebase user object to templates as 'user'.
    This replaces django.contrib.auth.context_processors.auth
    """
    if hasattr(request, 'user'):
        return {'user': request.user}
    return {}
