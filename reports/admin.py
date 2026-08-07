from django.contrib import admin

from .models import (
    RapportCNVZ,
    RapportGlobal,
    ConclusionGlobale,
)


admin.site.register(RapportCNVZ)
admin.site.register(RapportGlobal)
admin.site.register(ConclusionGlobale)