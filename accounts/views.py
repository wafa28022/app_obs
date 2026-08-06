from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def apres_connexion(request):
    role = request.user.role
    if role == 'region':
        return redirect('formulaire_region')
    elif role == "central":
        return redirect("upload_rapport_central")
    elif role == 'encadrement':
        return redirect('dashboard_encadrement')
    return redirect('login')