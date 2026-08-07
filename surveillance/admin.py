from django.contrib import admin

from .models import (
    Formulaire,
    Maladie,
    FormulaireMaladie,
    CasMaladie,
    DeclarationWNV,
    CasWNV,
    CasMAPI,
    SurveillanceSentinelle,
    Evenement,
    ConclusionIndicateurs,
    ConclusionEvenements,
)


admin.site.register(Formulaire)
admin.site.register(Maladie)
admin.site.register(FormulaireMaladie)
admin.site.register(CasMaladie)
admin.site.register(DeclarationWNV)
admin.site.register(CasWNV)
admin.site.register(CasMAPI)
admin.site.register(SurveillanceSentinelle)
admin.site.register(Evenement)
admin.site.register(ConclusionIndicateurs)
admin.site.register(ConclusionEvenements)