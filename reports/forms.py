from django import forms

from .models import RapportCNVZ


class RapportCNVZForm(forms.ModelForm):
    class Meta:
        model = RapportCNVZ

        fields = [
            "titre",
            "date_debut_semaine",
            "date_fin_semaine",
            "fichier_rapport",
        ]

        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Veille zoosanitaire semaine 32",
                }
            ),

            "date_debut_semaine": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "date_fin_semaine": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "fichier_rapport": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.ppt,.pptx",
                }
            ),
        }