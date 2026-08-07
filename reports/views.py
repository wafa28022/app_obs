from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from accounts.decorators import role_required

from .forms import RapportCNVZForm


@login_required
@role_required("cnvz")
def upload_rapport_cnvz(request):

    if request.method == "POST":
        form = RapportCNVZForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            rapport = form.save(commit=False)

            rapport.depose_par = request.user

            try:
                rapport.save()

                messages.success(
                    request,
                    "Le rapport CNVZ a été déposé avec succès."
                )

                return redirect("upload_rapport_cnvz")

            except IntegrityError:
                form.add_error(
                    None,
                    (
                        "Un rapport CNVZ existe déjà "
                        "pour cette semaine ISO."
                    )
                )

    else:
        form = RapportCNVZForm()

    return render(
        request,
        "reports/upload_rapport_cnvz.html",
        {
            "form": form,
        },
    )