from django import forms

from .models import Formulaire


class FormulairePrincipalForm(forms.ModelForm):
    class Meta:
        model = Formulaire

        fields = [
            "date_debut_semaine",
            "date_fin_semaine",
            "date_saisie",
        ]

        labels = {
            "date_debut_semaine": "Date de début de semaine",
            "date_fin_semaine": "Date de fin de semaine",
            "date_saisie": "Date de saisie",
        }
        widgets = {
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

            "date_saisie": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }