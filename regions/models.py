from django.db import models

class Region(models.Model):
    nom_gouvernorat = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom_gouvernorat


