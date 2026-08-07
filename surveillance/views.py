from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from accounts.decorators import role_required

from .forms import FormulairePrincipalForm


def construire_formulaire(request):
    if request.method == "POST":
        return FormulairePrincipalForm(request.POST)

    return FormulairePrincipalForm()


def enregistrer_formulaire(form, utilisateur):
    formulaire = form.save(commit=False)

    formulaire.utilisateur = utilisateur

    if utilisateur.role == "region":
        formulaire.region = utilisateur.region
    else:
        formulaire.region = None

    try:
        formulaire.save()

    except ValidationError as erreur:
        form.add_error(
            None,
            "Un formulaire existe déjà pour cette semaine ISO."
        )

        return None

    return formulaire

@login_required
@role_required("region")
def formulaire_region(request):
    form = construire_formulaire(request)

    if request.method == "POST" and form.is_valid():
        formulaire = enregistrer_formulaire(
            form,
            request.user,
        )

        if formulaire is not None:
            messages.success(
                request,
                (
                    "Formulaire créé avec succès - "
                    f"Semaine ISO {formulaire.semaine_iso}/"
                    f"{formulaire.annee_iso}."
                ),
            )

            return redirect("formulaire_region")
    return render(
        request,
        "surveillance/formulaire_principal.html",
        {
            "form": form,
            "type_declarant": "Région",
        },
    )


@login_required
@role_required("central_humain")
def formulaire_central(request):
    form = construire_formulaire(request)

    if request.method == "POST" and form.is_valid():
        formulaire = enregistrer_formulaire(
            form,
            request.user,
        )

        if formulaire is not None:
            messages.success(
                request,
                (
                    "Formulaire créé avec succès - "
                    f"Semaine ISO {formulaire.semaine_iso}/"
                    f"{formulaire.annee_iso}."
                ),
            )

            return redirect("formulaire_central")

    return render(
        request,
        "surveillance/formulaire_principal.html",
        {
            "form": form,
            "type_declarant": "Central humain",
        },
    )