from functools import wraps
from django.shortcuts import redirect

def role_required(*roles_autorises):
    def decorateur(vue):
        @wraps(vue)
        def vue_protegee(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles_autorises:
                return redirect('apres_connexion')
            return vue(request, *args, **kwargs)
        return vue_protegee
    return decorateur