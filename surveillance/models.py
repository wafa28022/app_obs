from django.db import models
from django.conf import settings
from regions.models import Region

STATUT_CHOICES = [
    ('brouillon', 'Brouillon'),
    ('soumis', 'Soumis'),
]

class FormulaireRegion(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='formulaires')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_rapport = models.DateField()
    semaine_iso = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    rapport_global = models.ForeignKey(
        'reports.RapportGlobal', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='formulaires_region'
    )

    def __str__(self):
        return f"Formulaire {self.region} - semaine {self.semaine_iso}"


class FormulaireCentral(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    regions = models.ManyToManyField(Region, related_name='formulaires_centraux')
    date_rapport = models.DateField()
    semaine_iso = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    rapport_global = models.ForeignKey(
        'reports.RapportGlobal', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='formulaires_central'
    )

    def __str__(self):
        return f"Formulaire Central - semaine {self.semaine_iso}"


class MaladieDeclaree(models.Model):
    formulaire_region = models.ForeignKey(FormulaireRegion, on_delete=models.CASCADE, null=True, blank=True, related_name='maladies')
    formulaire_central = models.ForeignKey(FormulaireCentral, on_delete=models.CASCADE, null=True, blank=True, related_name='maladies')
    nom_maladie = models.CharField(max_length=100)
    nb_cas = models.PositiveIntegerField(default=0)
    nb_deces = models.PositiveIntegerField(default=0)
    nb_hospitalises = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom_maladie


class Evenement(models.Model):
    formulaire_region = models.ForeignKey(FormulaireRegion, on_delete=models.CASCADE, null=True, blank=True, related_name='evenements')
    formulaire_central = models.ForeignKey(FormulaireCentral, on_delete=models.CASCADE, null=True, blank=True, related_name='evenements')
    type_evenement = models.CharField(max_length=100)
    statut = models.CharField(max_length=20)

    def __str__(self):
        return self.type_evenement


class ConclusionRegion(models.Model):
    formulaire_region = models.OneToOneField(FormulaireRegion, on_delete=models.CASCADE, related_name='conclusion')
    texte = models.TextField()