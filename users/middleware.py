class FirebaseUser:
    def __init__(self, email, username):
        self.email = email
        self.username = username
        self.is_authenticated = True
        self.first_name = ""
        self.last_name = ""
        
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

class AnonymousFirebaseUser:
    is_authenticated = False
    username = ''
    email = ''

class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        email = request.session.get('user_email')
        username = request.session.get('user_username')
        if email:
            user = FirebaseUser(email, username)
            user.first_name = request.session.get('user_first_name', '')
            user.last_name = request.session.get('user_last_name', '')
            request.user = user
        else:
            request.user = AnonymousFirebaseUser()
        return self.get_response(request)
