from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import role_required

@login_required
@role_required('region')
def formulaire_region(request):
    return render(request, 'surveillance/formulaire_region.html')

@login_required
@role_required('central')
def formulaire_central(request):
    return render(request, 'surveillance/formulaire_central.html')