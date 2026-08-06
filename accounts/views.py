from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def apres_connexion(request):
    role = request.user.role

    if role == "region":
        return redirect("formulaire_region")

    if role == "central_humain":
        return redirect("formulaire_central")

    if role == "cnvz":
        return redirect("upload_rapport_cnvz")

    if role == "encadrement":
        return redirect("dashboard_encadrement")

    return redirect("login")