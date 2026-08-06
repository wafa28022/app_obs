from django.db import models
from django.conf import settings
from regions.models import Region

STATUT_CHOICES = [
    ('brouillon', 'Brouillon'),
    ('soumis', 'Soumis'),
]

class RapportHebdomadaire(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='rapports')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_rapport = models.DateField()
    semaine_iso = models.PositiveIntegerField()
    annee = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    conclusion = models.TextField(
    blank=True
        )
    

    def __str__(self):
        return f"{self.region} - Semaine {self.semaine_iso}/{self.annee}"

class RapportCentral(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    semaine_iso = models.PositiveIntegerField()

    annee = models.PositiveIntegerField()

    fichier = models.FileField(
        upload_to="rapports_centraux/"
    )

    date_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Formulaire Central - semaine {self.semaine_iso}"


class MaladieDeclaree(models.Model):

    rapport = models.ForeignKey(
        RapportHebdomadaire,
        on_delete=models.CASCADE,
        related_name="maladies"
    )

    nom_maladie = models.CharField(max_length=100)

    nb_cas = models.PositiveIntegerField(default=0)

    nb_deces = models.PositiveIntegerField(default=0)

    nb_hospitalises = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom_maladie


class Evenement(models.Model):

    rapport = models.ForeignKey(
        RapportHebdomadaire,
        on_delete=models.CASCADE,
        related_name="evenements"
    )

    type_evenement = models.CharField(max_length=100)

    statut = models.CharField(max_length=20)

    def __str__(self):
        return self.type_evenement


