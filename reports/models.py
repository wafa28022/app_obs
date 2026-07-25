from django.db import models

class RapportGlobal(models.Model):
    periode = models.DateField()

    def __str__(self):
        return f"Rapport global - {self.periode}"


class ConclusionGlobale(models.Model):
    rapport_global = models.OneToOneField(RapportGlobal, on_delete=models.CASCADE, related_name='conclusion')
    texte = models.TextField()