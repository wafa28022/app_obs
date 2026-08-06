from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import role_required

@login_required
@role_required('encadrement')
def dashboard_encadrement(request):
    return render(request, 'dashboard/dashboard_encadrement.html')