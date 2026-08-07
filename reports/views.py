from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import role_required


@login_required
@role_required("cnvz")
def upload_rapport_cnvz(request):
    return render(
        request,
        "reports/upload_rapport_cnvz.html",
    )